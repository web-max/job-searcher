"""Draft outreach messages: proven template structures, rewritten in her voice,
linted for AI tells, saved to outbox/ for human review. Never sends anything.

Template structures come from docs/research/03-outreach-strategies.md
(Dalton's 6-point email, RISE, forwardable-email pattern, etc.).
"""
import re
from datetime import datetime, timezone

from . import humanize, llm, tracker, voice
from .paths import OUTBOX_DIR, TEMPLATES_DIR
from .settings import load_profile, load_settings

KINDS = {
    "connection_note": "LinkedIn connection request note (hard cap 300 characters)",
    "info_interview": "informational interview / coffee chat ask (15-20 min, insight not job leads)",
    "hiring_manager": "short note to the hiring manager after applying",
    "recruiter": "intro to an internal recruiter naming a specific open req",
    "referral_ask": "referral ask to someone she already talked to (with an explicit out)",
    "followup": "single polite bump, 7-10 days after silence",
    "thank_you": "thank-you within 24h of a call, naming one thing she learned and one action taken",
    "forwardable": "forwardable blurb a mutual contact can pass along without editing",
}

KIND_TO_LINT = {
    "connection_note": "linkedin_note",
    "info_interview": "linkedin_message",
    "hiring_manager": "linkedin_message",
    "recruiter": "linkedin_message",
    "referral_ask": "linkedin_message",
    "followup": "linkedin_note",
    "thank_you": "linkedin_message",
    "forwardable": "email",
}

SYSTEM = """You draft short job-search outreach messages AS the candidate, in her real
voice (profile provided). Rules that override everything else:
- Ask for insight and advice, never for a job or referral (unless kind=referral_ask,
  and then phrase it "would you feel comfortable referring me?" with an explicit out).
- One ask per message, phrased as a question. Concrete CTA (a 15-minute call, a
  specific question), never "let me know if interested".
- More than half the words should be about THEM, not her.
- The first sentence must contain a specific detail about the recipient or company
  from the provided context. If the context has no such detail, use the strongest
  available fact and keep it honest - never invent one.
- Respect the length limit for the message kind. Shorter is better.
- Plain words, her rhythm, no em dashes, no "not just X but Y", no rule-of-three
  triads, no corporate phrases, no flattery openers, no summary closers.
- Never fabricate experience, mutual connections, or facts. Only use what the
  profile and context state."""


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def draft(kind: str, person: str = "", person_role: str = "", company: str = "",
          job_id: str = None, context: str = "", channel: str = "linkedin") -> str:
    if kind not in KINDS:
        raise SystemExit(f"unknown kind '{kind}'; options: {', '.join(KINDS)}")

    profile = load_profile()
    settings = load_settings()
    vp = voice.get_profile()

    job = tracker.get_job(job_id) if job_id else None
    if job and not company:
        company = job["company"]

    template_path = TEMPLATES_DIR / f"{kind}.md"
    template = template_path.read_text() if template_path.exists() else ""

    user = f"""VOICE PROFILE:
{vp}

CANDIDATE FACTS (only source of truth about her):
{profile.get('summary', '')}
Based in: {profile.get('location')} ({profile.get('timezone', '')})
Languages: {', '.join(profile.get('languages', [])) or 'not specified'}
Target roles: {', '.join(profile.get('target_titles', []))}
Links: {profile.get('links', {})}
Note: if she is outside the recipient's country and timezone overlap is genuinely
good (e.g. Peru is UTC-5, same hours as US Eastern/Central), that is a true,
useful detail worth one short clause when relevant. Never oversell it.

MESSAGE KIND: {kind} - {KINDS[kind]}
CHANNEL: {channel}
RECIPIENT: {person or 'unknown'} ({person_role or 'role unknown'}) at {company or 'unknown company'}
{f"JOB: {job['title']} - {job['url']}" if job else ""}
{f"JOB DESCRIPTION (excerpt): {job['description'][:800]}" if job else ""}

CONTEXT / RESEARCH NOTES (specific details to anchor the first sentence):
{context or '(none provided - keep the message honest and general, and note at the top of your output that adding one specific detail about the recipient would roughly double the reply rate)'}

PROVEN TEMPLATE STRUCTURE (structure to follow, words to replace with hers):
{template}

Write the message now. Output only the message text."""

    text = llm.complete(SYSTEM, user, max_tokens=600, temperature=0.8).strip()

    hcfg = settings.get("humanizer", {})
    final, findings, passed = humanize.polish(
        text, vp, kind=KIND_TO_LINT.get(kind, "linkedin_message"),
        max_passes=hcfg.get("max_rewrite_passes", 2),
        fail_on=tuple(hcfg.get("fail_on", ["high"])),
    )

    # volume check - warn, don't block; the human decides
    counts = tracker.counts_today()
    cap = settings.get("volumes", {}).get("max_new_outreach_per_day", 5)
    volume_note = ""
    if counts["messaged"] >= cap:
        volume_note = (f"\n> NOTE: already logged {counts['messaged']} outreach messages today "
                       f"(cap {cap}). Consider saving this one for tomorrow - quality and pacing win.\n")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    fname = OUTBOX_DIR / f"{ts}-{kind}-{_slug(person or company or 'draft')}.md"
    fname.write_text(f"""# {kind} -> {person or '?'} @ {company or '?'}

- channel: {channel}
- job: {job['title'] + ' (' + job['id'] + ')' if job else 'n/a'}
- lint: {'PASSED' if passed else 'STILL HAS ISSUES - edit before sending'}
{volume_note}
## Message (copy, read aloud once, edit anything that doesn't sound like you, then send)

{final}

## Linter findings on final draft
{humanize.format_findings(findings)}

## Before sending checklist
- [ ] Read it aloud - rewrite anything you stumble on
- [ ] The first sentence has a real, specific detail (swap test: would this message make sense sent to someone else? If yes, it's too generic)
- [ ] You'd be happy to defend every word as your own
- [ ] Log it after sending: python -m agent log --contact "{person}" --event messaged
""")
    print(f"draft written to {fname}")
    if not passed:
        print("warning: draft still has high-severity lint findings; edit before sending")
    return str(fname)
