"""Assisted apply: fill a non-LinkedIn ATS application form in a local browser, then STOP.

The rule (see CLAUDE.md "Human intelligence in the loop"): machines do the
mechanical prep, the human does the judgment. This module fills the form and
lands her on a checkable, filled-out page; it NEVER clicks submit. She reads
every field, fixes what's wrong, answers what was skipped, and presses submit
herself.

Hard limits, not preferences:
  - LinkedIn is never touched (account-ban risk).
  - Nothing here ever clicks a submit button or presses Enter in a form.
  - EEO / demographic / salary questions are always left for the human.

Off by default. Turn on with apply.form_autofill in config/settings.yaml or
the switch on the app's Help page (which sets FORM_AUTOFILL in .env).
"""
import os
import re
import sys
from urllib.parse import urlparse

from . import tracker
from .paths import OUTBOX_DIR

# Never automate these, on or off, no exceptions.
BLOCKED_HOST_SUFFIXES = ("linkedin.com",)

# Hosts we recognize as real application forms. Anything else non-LinkedIn is
# attempted with a warning (the posting url is often a listing, not the form).
KNOWN_ATS_SUFFIXES = ("greenhouse.io", "lever.co", "ashbyhq.com",
                      "workable.com", "myworkdayjobs.com")

# Questions a machine must not answer: demographics, EEO, comp expectations.
SKIP_PATTERNS = re.compile(
    r"gender|race|ethnic|veteran|disab|pronoun|hispanic|latino|lgbt|orientation"
    r"|demographic|eeo|salary|compensation|desired pay|sponsor",
    re.I)


def autofill_enabled(settings):
    """FORM_AUTOFILL env (set by the Help page switch) overrides settings.yaml."""
    env = os.getenv("FORM_AUTOFILL")
    if env is not None:
        return env.strip().lower() in ("1", "true", "yes", "on")
    return bool((settings.get("apply") or {}).get("form_autofill", False))


def blocked_reason(url):
    host = (urlparse(url).hostname or "").lower()
    for suffix in BLOCKED_HOST_SUFFIXES:
        if host == suffix or host.endswith("." + suffix):
            return ("LinkedIn forms are never automated - it's an account-ban "
                    "risk. Apply there by hand.")
    return None


def is_known_ats(url):
    host = (urlparse(url).hostname or "").lower()
    return any(host == s or host.endswith("." + s) for s in KNOWN_ATS_SUFFIXES)


def latest_cover_note(job_id):
    """Cover note from the newest tailor kit for this job, or ''."""
    for kit in sorted(OUTBOX_DIR.glob(f"*-tailor-{job_id}.md"), reverse=True):
        m = re.search(r"## Cover note\n(.*?)(?=\n## |\Z)", kit.read_text(), re.S)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""


def _split_name(profile):
    parts = (profile.get("name") or "").split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])


def _match_key(blob, kind):
    if kind == "textarea":
        if re.search(r"cover|why .*(join|interest|us|compan)|motivat", blob):
            return "cover_letter"
        return None
    for pattern, key in (
        (r"first[\s_-]*name|given[\s_-]*name|given-name", "first_name"),
        (r"last[\s_-]*name|family[\s_-]*name|family-name|surname", "last_name"),
        (r"full[\s_-]*name|\bname\b", "full_name"),
        (r"e-?mail", "email"),
        (r"phone|mobile|\btel\b", "phone"),
        (r"location|city|address", "location"),
        (r"linkedin", "linkedin"),
        (r"website|portfolio|\burl\b", "website"),
    ):
        if re.search(pattern, blob):
            return key
    return None


def plan_fill(fields, profile, cover_note=""):
    """Pure mapping from form field descriptors to values. No browser here.

    fields: dicts with idx, kind ('text'|'textarea'|'file'), name, id, label,
    placeholder, autocomplete, type. Returns (plan, skipped): plan is
    [(field, value)], skipped is [(field, reason)].
    """
    contact = profile.get("contact") or {}
    links = profile.get("links") or {}
    first, last = _split_name(profile)
    values = {
        "first_name": first,
        "last_name": last,
        "full_name": profile.get("name") or "",
        "email": contact.get("email") or "",
        "phone": contact.get("phone") or "",
        "location": profile.get("location") or "",
        "linkedin": contact.get("linkedin_url") or links.get("linkedin") or "",
        "website": contact.get("website") or links.get("portfolio") or "",
        "cover_letter": cover_note,
    }
    resume = contact.get("resume_path") or ""
    plan, skipped = [], []
    for f in fields:
        blob = " ".join(str(f.get(k) or "") for k in
                        ("name", "id", "label", "placeholder", "autocomplete",
                         "type")).lower()
        if SKIP_PATTERNS.search(blob):
            skipped.append((f, "left for the human (judgment/demographic question)"))
            continue
        if f.get("kind") == "file":
            if resume and re.search(r"resume|cv", blob):
                plan.append((f, resume))
            else:
                skipped.append((f, "file upload - attach it yourself"))
            continue
        key = _match_key(blob, f.get("kind"))
        if key and values.get(key):
            plan.append((f, values[key]))
        else:
            skipped.append((f, "no confident match - fill by hand"))
    return plan, skipped


# Tags each visible input/textarea with data-agent-idx and returns descriptors.
_COLLECT_JS = """
() => {
  const out = [];
  let i = 0;
  for (const el of document.querySelectorAll('input, textarea')) {
    const type = (el.getAttribute('type') ||
                  (el.tagName === 'TEXTAREA' ? 'textarea' : 'text')).toLowerCase();
    if (['hidden', 'submit', 'button', 'checkbox', 'radio', 'image',
         'reset', 'search'].includes(type)) continue;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden') continue;
    const idx = 'agent-' + (i++);
    el.setAttribute('data-agent-idx', idx);
    let label = '';
    if (el.labels && el.labels.length) label = el.labels[0].innerText;
    else if (el.closest('label')) label = el.closest('label').innerText;
    out.push({idx: idx,
              kind: type === 'textarea' ? 'textarea'
                    : (type === 'file' ? 'file' : 'text'),
              type: type, name: el.name || '', id: el.id || '',
              label: (label || '').trim().slice(0, 120),
              placeholder: el.placeholder || '',
              autocomplete: el.getAttribute('autocomplete') || ''});
  }
  return out;
}
"""


def _describe(f):
    return f.get("label") or f.get("name") or f.get("placeholder") or f.get("id") or f.get("idx")


def run(job_id, settings, profile, url=None):
    if not autofill_enabled(settings):
        sys.exit("Assisted apply is switched off. Turn it on with the switch on "
                 "the app's Help page, or set apply.form_autofill: true in "
                 "config/settings.yaml.")
    job = tracker.get_job(job_id)
    if not job:
        sys.exit(f"job {job_id} not found - run discover, or check the id")
    target = url or job["url"]
    reason = blocked_reason(target)
    if reason:
        sys.exit(reason)
    if not is_known_ats(target):
        print("note: not a recognized ATS (Greenhouse/Lever/Ashby/Workable/"
              "Workday). The posting page may not be the application form - "
              "if nothing gets filled, pass the real form url with --url.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright is not installed. One-time setup:\n"
                 "  pip install playwright\n  playwright install chromium")

    cover = latest_cover_note(job_id)
    if not cover:
        print(f"no application kit found for {job_id} - cover letter fields "
              f"will be left blank (run: python -m agent tailor --job {job_id})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(target, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)  # let ATS scripts render the form

        filled = 0
        skipped_msgs = []
        for frame in page.frames:
            try:
                fields = frame.evaluate(_COLLECT_JS)
            except Exception:
                continue
            if not fields:
                continue
            plan, skipped = plan_fill(fields, profile, cover)
            for f, value in plan:
                loc = frame.locator(f'[data-agent-idx="{f["idx"]}"]')
                try:
                    if f["kind"] == "file":
                        loc.set_input_files(value)
                    else:
                        loc.fill(value)
                    filled += 1
                    print(f"  filled: {_describe(f)}")
                except Exception as e:
                    skipped_msgs.append(f"  couldn't fill {_describe(f)}: {e.__class__.__name__}")
            skipped_msgs += [f"  skipped: {_describe(f)} ({why})" for f, why in skipped]

        print(f"\nfilled {filled} field(s); left {len(skipped_msgs)} for you:")
        for m in skipped_msgs:
            print(m)
        print("\nThis tool NEVER submits. In the browser window:")
        print("  1. Read every filled field - fix anything that isn't true or isn't you")
        print("  2. Answer the skipped questions (dropdowns, demographics, uploads)")
        print("  3. Press submit yourself, then close the browser window")
        print(f"  4. Log it: python -m agent log --job {job_id} --event applied")
        try:
            page.wait_for_event("close", timeout=0)  # stay alive until she closes it
        except Exception:
            pass
