"""Local web GUI - the friendly face of the agent for a non-technical user.

Run with:  python -m agent gui   (opens http://127.0.0.1:7333 in the browser)

Design rules:
- Everything the CLI can do, one click can do.
- Nothing ever sends. Drafts open for review with a copy button; SHE pastes
  them into LinkedIn/email and clicks send there, then hits "I sent it".
- Plain language, no jargon, encouraging tone. The pipeline view shows motion
  (replies, calls) as wins, because a job search is a marathon.
"""
import html
import io
import threading
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from flask import Flask, redirect, request, url_for

from agent import tracker
from agent.paths import OUTBOX_DIR, VOICE_PROFILE_PATH, VOICE_CORPUS_DIR
from agent.settings import load_profile, load_settings

app = Flask(__name__)

# one background job at a time; state shown on the dashboard
_task = {"name": None, "log": "", "running": False, "error": None}


def _run_bg(name, fn):
    if _task["running"]:
        return False
    _task.update({"name": name, "log": "", "running": True, "error": None})

    def wrapper():
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                fn()
        except Exception:
            _task["error"] = traceback.format_exc(limit=3)
        finally:
            _task["log"] = buf.getvalue()[-4000:]
            _task["running"] = False

    threading.Thread(target=wrapper, daemon=True).start()
    return True


STYLE = """
<style>
:root { --bg:#f7f6f3; --card:#fff; --ink:#2d2a26; --muted:#8a8578; --accent:#2f6f4f;
        --accent2:#b25b2a; --line:#e6e2d8; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; background:var(--bg); color:var(--ink);
       margin:0; line-height:1.55; }
nav { background:var(--card); border-bottom:1px solid var(--line); padding:14px 28px;
      display:flex; gap:22px; align-items:baseline; flex-wrap:wrap; }
nav .brand { font-size:1.25rem; font-weight:bold; color:var(--accent); margin-right:8px; }
nav a { color:var(--ink); text-decoration:none; font-size:.98rem; }
nav a:hover { color:var(--accent); }
main { max-width:960px; margin:26px auto; padding:0 20px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px;
        padding:18px 22px; margin-bottom:18px; }
h1 { font-size:1.5rem; margin:.2em 0 .6em; } h2 { font-size:1.15rem; margin:.2em 0 .5em; }
.muted { color:var(--muted); font-size:.92rem; }
.btn { display:inline-block; background:var(--accent); color:#fff; border:none; border-radius:7px;
       padding:8px 16px; font-size:.95rem; cursor:pointer; text-decoration:none;
       font-family:inherit; }
.btn.secondary { background:#fff; color:var(--accent); border:1px solid var(--accent); }
.btn.warn { background:var(--accent2); }
.btn:disabled { background:var(--muted); cursor:default; }
table { width:100%; border-collapse:collapse; font-size:.95rem; }
td, th { text-align:left; padding:7px 8px; border-bottom:1px solid var(--line); vertical-align:top; }
.score { font-weight:bold; color:var(--accent); }
.pill { display:inline-block; padding:1px 9px; border-radius:99px; font-size:.8rem;
        background:var(--line); }
pre { white-space:pre-wrap; background:#faf9f6; border:1px solid var(--line);
      border-radius:8px; padding:14px; font-family:inherit; font-size:.97rem; }
input, select, textarea { width:100%; padding:8px; border:1px solid var(--line); border-radius:7px;
      font-family:inherit; font-size:.95rem; background:#fff; }
label { display:block; margin:10px 0 3px; font-size:.92rem; color:var(--muted); }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:0 18px; }
.banner { background:#eef4ef; border:1px solid #cfe0d4; border-radius:8px; padding:10px 14px;
          margin-bottom:16px; font-size:.95rem; }
.warnbox { background:#faf0e8; border-color:#e8d5c4; }
@media (max-width:640px){ .grid2 { grid-template-columns:1fr; } }
</style>
"""


def page(title, body, refresh=False):
    meta = '<meta http-equiv="refresh" content="3">' if refresh else ""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>{meta}{STYLE}</head><body>
<nav><span class="brand">Job Search HQ</span>
<a href="/">Today</a> <a href="/jobs">Jobs</a> <a href="/outbox">Drafts to send</a>
<a href="/outreach">Write a message</a> <a href="/people">People</a> <a href="/help">Help</a></nav>
<main>{body}</main></body></html>"""


def esc(x):
    return html.escape(str(x if x is not None else ""))


# ------------------------------------------------------------------ dashboard

@app.route("/")
def dashboard():
    settings = load_settings()
    vols = settings.get("volumes", {})
    min_score = settings.get("ranking", {}).get("min_score_to_surface", 65)
    counts = tracker.counts_today()
    snap = tracker.pipeline_snapshot()
    top = tracker.top_jobs(min_score=min_score, limit=8)
    due = tracker.followups_due(vols.get("followup_after_days", 6), vols.get("max_followups", 2))

    task_html = ""
    if _task["running"]:
        task_html = f'<div class="banner">Working on <b>{esc(_task["name"])}</b>… this page refreshes itself.</div>'
    elif _task["name"]:
        status = "hit a snag" if _task["error"] else "finished"
        detail = f'<pre>{esc(_task["error"] or _task["log"] or "done")}</pre>' if (_task["error"] or _task["log"]) else ""
        task_html = f'<div class="banner{" warnbox" if _task["error"] else ""}">Last run: <b>{esc(_task["name"])}</b> {status}. {detail}</div>'

    import os
    key_note = ""
    if not (os.getenv("DEEPSEEK_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("OPENAI_API_KEY") or os.getenv("MOCK_LLM")):
        key_note = ('<div class="banner warnbox">No AI key set yet, so "Score jobs" and drafting '
                    'are off. Put your DeepSeek key in the <code>.env</code> file (see Help).</div>')

    rows = "".join(
        f'<tr><td class="score">{esc(j["score"])}</td>'
        f'<td><a href="/job/{esc(j["id"])}">{esc(j["title"])}</a><br>'
        f'<span class="muted">{esc(j["company"])} · {esc(j["location"] or "location n/a")} · posted {esc(j["posted_at"] or "?")}</span></td></tr>'
        for j in top) or '<tr><td colspan="2" class="muted">Nothing yet - click "Find new jobs", then "Score jobs".</td></tr>'

    due_rows = "".join(
        f'<tr><td>{esc(c["name"])} <span class="muted">({esc(c["role"])} at {esc(c["company"])})</span></td>'
        f'<td class="muted">last touch {esc((c["last_touch"] or "")[:10])}</td>'
        f'<td><a class="btn secondary" href="/outreach?kind=followup&person={esc(c["name"])}&company={esc(c["company"])}">draft a nudge</a></td></tr>'
        for c in due) or '<tr><td colspan="3" class="muted">No follow-ups due. Nice and clear.</td></tr>'

    wins = (snap["contacts"].get("replied", 0) + snap["contacts"].get("call_done", 0)
            + snap["jobs"].get("interviewing", 0) + snap["jobs"].get("offer", 0))

    body = f"""
{key_note}{task_html}
<div class="card"><h1>Today</h1>
<p>Applications logged today: <b>{counts['applied']}</b> / {vols.get('max_applications_per_day', 5)} ·
Messages logged today: <b>{counts['messaged']}</b> / {vols.get('max_new_outreach_per_day', 5)}
<span class="muted">(small daily numbers on purpose - quality wins)</span></p>
<form method="post" action="/run/discover" style="display:inline">
  <button class="btn" {"disabled" if _task["running"] else ""}>1 · Find new jobs</button></form>
<form method="post" action="/run/rank" style="display:inline">
  <button class="btn" {"disabled" if _task["running"] else ""}>2 · Score jobs</button></form>
<a class="btn secondary" href="/jobs">3 · Review matches</a>
</div>
<div class="card"><h2>Best matches right now</h2><table>{rows}</table></div>
<div class="card"><h2>Follow-ups due</h2>
<p class="muted">A gentle nudge a week later gets almost half of all replies. One nudge only.</p>
<table>{due_rows}</table></div>
<div class="card"><h2>Pipeline</h2>
<p>{'; '.join(f"{v} {k}" for k, v in snap['jobs'].items()) or 'no jobs tracked yet'}<br>
<span class="muted">People: {'; '.join(f"{v} {k}" for k, v in snap['contacts'].items()) or 'none yet'}</span></p>
<p>Momentum score (replies + calls + interviews): <b>{wins}</b> - these are the numbers that predict offers.</p></div>
"""
    return page("Today - Job Search HQ", body, refresh=_task["running"])


@app.route("/run/<what>", methods=["POST"])
def run_task(what):
    profile, settings = load_profile(), load_settings()
    if what == "discover":
        from agent import discover
        _run_bg("finding new jobs", lambda: discover.run(profile, settings))
    elif what == "rank":
        from agent import rank
        _run_bg("scoring jobs", lambda: rank.run(profile, settings))
    elif what == "voice":
        from agent import voice
        _run_bg("studying your writing style", voice.build_profile)
    return redirect(url_for("dashboard"))


# ------------------------------------------------------------------ jobs

@app.route("/jobs")
def jobs():
    settings = load_settings()
    min_score = settings.get("ranking", {}).get("min_score_to_surface", 65)
    with tracker.conn() as c:
        rows = [dict(r) for r in c.execute(
            """SELECT * FROM jobs WHERE status NOT IN ('rejected','dropped')
               ORDER BY CASE WHEN score IS NULL THEN 1 ELSE 0 END, score DESC, posted_at DESC
               LIMIT 100""")]
    trs = "".join(
        f'<tr><td class="score">{esc(j["score"] if j["score"] is not None else "-")}</td>'
        f'<td><a href="/job/{esc(j["id"])}">{esc(j["title"])}</a><br>'
        f'<span class="muted">{esc(j["company"])} · {esc(j["location"] or "")}</span></td>'
        f'<td><span class="pill">{esc(j["status"])}</span></td>'
        f'<td class="muted">{esc(j["posted_at"] or "")}</td></tr>'
        for j in rows) or '<tr><td colspan="4" class="muted">No jobs yet - go to Today and click "Find new jobs".</td></tr>'
    body = f"""<div class="card"><h1>All tracked jobs</h1>
<p class="muted">Scores {min_score}+ are worth a look; 75+ deserve a same-day tailored application.</p>
<table><tr><th>Score</th><th>Role</th><th>Status</th><th>Posted</th></tr>{trs}</table></div>"""
    return page("Jobs", body)


@app.route("/job/<job_id>")
def job_detail(job_id):
    j = tracker.get_job(job_id)
    if not j:
        return page("Not found", '<div class="card">Job not found.</div>')
    body = f"""<div class="card">
<h1>{esc(j['title'])}</h1>
<p>{esc(j['company'])} · {esc(j['location'] or 'location n/a')} · posted {esc(j['posted_at'] or '?')}
· <span class="pill">{esc(j['status'])}</span></p>
<p><span class="score">Score: {esc(j['score'] if j['score'] is not None else 'not scored yet')}</span>
<span class="muted">{esc(j['score_reason'] or '')}</span></p>
<p><a class="btn secondary" href="{esc(j['url'])}" target="_blank">Open the real posting ↗</a>
<form method="post" action="/job/{esc(job_id)}/tailor" style="display:inline">
<button class="btn" {"disabled" if _task["running"] else ""}>Build my application kit</button></form>
<a class="btn" href="/outreach?job={esc(job_id)}&company={esc(j['company'])}">Write outreach for this job</a>
</p>
<form method="post" action="/job/{esc(job_id)}/event" style="display:inline">
<button class="btn secondary" name="event" value="applied">I applied ✓</button>
<button class="btn warn" name="event" value="dropped">Not for me</button></form>
</div>
<div class="card"><h2>Posting text</h2><pre>{esc(j['description'][:5000])}</pre></div>"""
    return page(j["title"], body)


@app.route("/job/<job_id>/tailor", methods=["POST"])
def job_tailor(job_id):
    from agent import tailor
    _run_bg("building the application kit (find it under Drafts when done)",
            lambda: tailor.run(job_id))
    return redirect(url_for("dashboard"))


@app.route("/job/<job_id>/event", methods=["POST"])
def job_event(job_id):
    ev = request.form.get("event")
    if ev == "applied":
        tracker.log_event("applied", job_id=job_id)
    elif ev == "dropped":
        tracker.set_status(job_id, "dropped")
    return redirect(url_for("jobs"))


# ------------------------------------------------------------------ outreach

KIND_LABELS = {
    "info_interview": "Ask someone about their job (coffee chat)",
    "connection_note": "LinkedIn connection request note",
    "hiring_manager": "Note to the hiring manager (after applying)",
    "recruiter": "Note to the company's recruiter",
    "referral_ask": "Ask for a referral (someone you've talked to)",
    "followup": "Gentle follow-up nudge",
    "thank_you": "Thank-you after a call",
    "forwardable": "Blurb a friend can forward to introduce you",
}


@app.route("/outreach")
def outreach_form():
    pre = {k: request.args.get(k, "") for k in ("kind", "person", "company", "job")}
    opts = "".join(f'<option value="{k}" {"selected" if pre["kind"] == k else ""}>{v}</option>'
                   for k, v in KIND_LABELS.items())
    body = f"""<div class="card"><h1>Write a message</h1>
<p class="muted">The draft lands under "Drafts to send" for you to review. Nothing is sent for you, ever.</p>
<form method="post" action="/outreach">
<label>What kind of message?</label><select name="kind">{opts}</select>
<div class="grid2">
<div><label>Their name</label><input name="person" value="{esc(pre['person'])}" placeholder="Jane Doe"></div>
<div><label>Their role</label><input name="person_role" placeholder="Customer Success Manager"></div>
<div><label>Company</label><input name="company" value="{esc(pre['company'])}"></div>
<div><label>Job id (optional, from the Jobs page)</label><input name="job" value="{esc(pre['job'])}"></div>
</div>
<label>The important part: one specific, true detail about them</label>
<textarea name="context" rows="3" placeholder="e.g. her post last week about onboarding playbooks; we both worked in hospitality before tech; they just launched X"></textarea>
<p class="muted">Messages that open with a real detail get roughly double the replies. If you don't have one, spend 2 minutes on their LinkedIn profile first - it's the highest-paid 2 minutes of the day.</p>
<label>Where will you send it?</label>
<select name="channel"><option value="linkedin">LinkedIn</option><option value="email">Email</option></select>
<p><button class="btn" {"disabled" if _task["running"] else ""}>Draft it</button></p>
</form></div>"""
    return page("Write a message", body)


@app.route("/outreach", methods=["POST"])
def outreach_post():
    from agent import outreach
    f = {k: request.form.get(k, "").strip() for k in
         ("kind", "person", "person_role", "company", "job", "context", "channel")}
    if f["person"] and not tracker.find_contact(f["person"]):
        rel = {"hiring_manager": "hiring_manager", "recruiter": "recruiter"}.get(f["kind"], "employee")
        tracker.add_contact(f["person"], company=f["company"], role=f["person_role"],
                            relationship=rel, job_id=f["job"] or None)
    _run_bg(f"drafting the {KIND_LABELS.get(f['kind'], 'message')}",
            lambda: outreach.draft(f["kind"], person=f["person"], person_role=f["person_role"],
                                   company=f["company"], job_id=f["job"] or None,
                                   context=f["context"], channel=f["channel"]))
    return redirect(url_for("dashboard"))


# ------------------------------------------------------------------ outbox

@app.route("/outbox")
def outbox():
    files = sorted(OUTBOX_DIR.glob("*.md"), reverse=True)
    rows = "".join(
        f'<tr><td><a href="/outbox/{esc(p.name)}">{esc(p.name)}</a></td>'
        f'<td class="muted">{p.stat().st_size // 1024 or 1} KB</td></tr>'
        for p in files) or '<tr><td class="muted">No drafts yet.</td></tr>'
    body = f"""<div class="card"><h1>Drafts to send</h1>
<p class="muted">Open a draft, read it aloud once, edit anything that doesn't sound like you,
copy it, send it yourself, then click "I sent it" so follow-ups get tracked.</p>
<table>{rows}</table></div>"""
    return page("Drafts", body)


@app.route("/outbox/<name>")
def outbox_view(name):
    path = OUTBOX_DIR / Path(name).name  # Path(name).name blocks traversal
    if not path.exists() or path.suffix != ".md":
        return page("Not found", '<div class="card">Draft not found.</div>')
    content = path.read_text()
    # crude extraction of the message body for the copy box
    msg = content
    if "## Message" in content:
        msg = content.split("## Message", 1)[1].split("##", 1)[0]
        msg = "\n".join(msg.splitlines()[1:]).strip()
    body = f"""<div class="card"><h1>{esc(name)}</h1>
<textarea id="msg" rows="{min(14, msg.count(chr(10)) + 4)}">{esc(msg)}</textarea>
<p><button class="btn" onclick="navigator.clipboard.writeText(document.getElementById('msg').value).then(()=>this.textContent='Copied ✓')">Copy message</button>
<form method="post" action="/outbox/{esc(name)}/sent" style="display:inline">
<button class="btn secondary">I sent it ✓</button></form>
<form method="post" action="/outbox/{esc(name)}/delete" style="display:inline">
<button class="btn warn" onclick="return confirm('Delete this draft?')">Delete draft</button></form></p>
</div>
<div class="card"><h2>Full draft file (checklist included)</h2><pre>{esc(content)}</pre></div>"""
    return page(name, body)


@app.route("/outbox/<name>/sent", methods=["POST"])
def outbox_sent(name):
    # filename shape: YYYYMMDD-HHMM-kind-person-slug.md
    stem = Path(name).stem
    parts = stem.split("-", 3)
    kind = parts[2] if len(parts) > 2 else "message"
    slug = parts[3] if len(parts) > 3 else ""
    contact = tracker.find_contact(slug.replace("-", " ")) if slug else None
    event = "followed_up" if kind == "followup" else "messaged"
    tracker.log_event(event, contact_id=contact["id"] if contact else None,
                      detail=f"sent draft {name}")
    sent_dir = OUTBOX_DIR / "sent"
    sent_dir.mkdir(exist_ok=True)
    (OUTBOX_DIR / Path(name).name).rename(sent_dir / Path(name).name)
    return redirect(url_for("outbox"))


@app.route("/outbox/<name>/delete", methods=["POST"])
def outbox_delete(name):
    path = OUTBOX_DIR / Path(name).name
    if path.exists():
        path.unlink()
    return redirect(url_for("outbox"))


# ------------------------------------------------------------------ people

@app.route("/people")
def people():
    with tracker.conn() as c:
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM contacts ORDER BY updated_at DESC LIMIT 100")]
    trs = "".join(
        f'<tr><td>{esc(c["name"])}</td><td class="muted">{esc(c["role"] or "")} @ {esc(c["company"] or "")}</td>'
        f'<td><span class="pill">{esc(c["status"])}</span></td>'
        f'<td><form method="post" action="/people/{c["id"]}/event">'
        f'<button class="btn secondary" name="event" value="replied">replied ✓</button> '
        f'<button class="btn secondary" name="event" value="call">had a call ✓</button></form></td></tr>'
        for c in rows) or '<tr><td colspan="4" class="muted">No people tracked yet - they get added when you draft messages.</td></tr>'
    body = f"""<div class="card"><h1>People</h1>
<p class="muted">Everyone you've reached out to. Mark replies and calls - those are the wins that turn into referrals.</p>
<table>{trs}</table></div>"""
    return page("People", body)


@app.route("/people/<int:cid>/event", methods=["POST"])
def people_event(cid):
    ev = request.form.get("event")
    if ev == "replied":
        tracker.log_event("replied", contact_id=cid)
    elif ev == "call":
        tracker.log_event("call", contact_id=cid)
        tracker.set_contact_status(cid, "call_done")
    return redirect(url_for("people"))


# ------------------------------------------------------------------ help

@app.route("/help")
def help_page():
    voice_built = VOICE_PROFILE_PATH.exists()
    n_corpus = len([p for p in VOICE_CORPUS_DIR.iterdir() if p.name != "README.md"]) \
        if VOICE_CORPUS_DIR.exists() else 0
    body = f"""<div class="card"><h1>How this works</h1>
<ol>
<li><b>Find new jobs</b> pulls fresh postings from real job feeds and your target companies' own career pages.</li>
<li><b>Score jobs</b> has the AI read each posting against your profile and score the fit 0-100, with a reason.</li>
<li><b>Application kit</b> writes honest, tailored resume-bullet suggestions and a short cover note for one job.</li>
<li><b>Messages</b> are drafted in <i>your</i> writing style, checked against a list of "sounds like a robot" patterns, and parked under Drafts. You always send them yourself - that's what keeps them genuine (and your accounts safe).</li>
<li>After you send or apply, click the ✓ buttons so the app remembers to remind you about follow-ups.</li>
</ol>
<p>The daily rhythm that works: <b>1-3 tailored applications + 2-5 real messages</b>. That's it.
More than that becomes spray, and spray doesn't get replies. Replies and calls are the real score.</p></div>
<div class="card"><h2>Your writing style</h2>
<p>Status: {"learned from your writing ✓" if voice_built else f"<b>not built yet</b> - {n_corpus} sample file(s) in the folder"}</p>
<p>Put 20+ examples of your own writing (sent emails, longer texts) in the <code>voice/corpus/</code>
folder, then click the button. The drafts will start sounding like you instead of like a bot.</p>
<form method="post" action="/run/voice"><button class="btn" {"disabled" if _task["running"] else ""}>Learn my writing style</button></form></div>
<div class="card"><h2>Setup notes</h2>
<p>The AI key lives in the <code>.env</code> file next to this app. DeepSeek is the cheap default
(about a dollar a month of usage at this volume): create a key at platform.deepseek.com, then put
<code>DEEPSEEK_API_KEY=sk-...</code> in <code>.env</code> and restart the app.</p>
<p>Windows quick start is in <code>docs/setup-windows.md</code>. The strategy and the research
behind all of this: <code>docs/playbook.md</code>.</p></div>"""
    return page("Help", body)


def main(host="127.0.0.1", port=7333, open_browser=True):
    if open_browser:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
