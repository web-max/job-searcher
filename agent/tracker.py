"""SQLite pipeline tracker: jobs, contacts, events.

Job statuses:  new -> ranked -> shortlisted -> applied -> interviewing -> offer
               (or: rejected, dropped)
Contact statuses: found -> messaged -> replied -> call_done -> referred
"""
import sqlite3
from datetime import datetime, timezone

from .paths import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    source TEXT, company TEXT, title TEXT, url TEXT,
    location TEXT, description TEXT, posted_at TEXT, salary TEXT,
    status TEXT DEFAULT 'new',
    score INTEGER, score_reason TEXT,
    created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, company TEXT, role TEXT,
    linkedin_url TEXT, email TEXT,
    relationship TEXT,           -- employee | hiring_manager | recruiter | mutual
    job_id TEXT REFERENCES jobs(id),
    status TEXT DEFAULT 'found',
    notes TEXT,
    created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    job_id TEXT, contact_id INTEGER,
    kind TEXT,                   -- applied | messaged | followed_up | replied | call | rejected | offer | note
    detail TEXT
);
"""


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def upsert_jobs(jobs: list) -> int:
    """Insert new jobs; leave existing rows (and their status/score) alone."""
    new = 0
    with conn() as c:
        for j in jobs:
            cur = c.execute(
                """INSERT OR IGNORE INTO jobs
                   (id, source, company, title, url, location, description,
                    posted_at, salary, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (j["id"], j["source"], j["company"], j["title"], j["url"],
                 j["location"], j["description"], j["posted_at"], j["salary"],
                 _now(), _now()),
            )
            new += cur.rowcount
    return new


def unranked_jobs(limit=200):
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM jobs WHERE status='new' ORDER BY posted_at DESC LIMIT ?", (limit,))]


def set_score(job_id, score, reason):
    with conn() as c:
        c.execute(
            "UPDATE jobs SET score=?, score_reason=?, status='ranked', updated_at=? WHERE id=?",
            (score, reason, _now(), job_id),
        )


def set_status(job_id, status):
    with conn() as c:
        cur = c.execute(
            "UPDATE jobs SET status=?, updated_at=? WHERE id=?", (status, _now(), job_id))
        return cur.rowcount


def get_job(job_id):
    with conn() as c:
        r = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(r) if r else None


def top_jobs(min_score=65, limit=25):
    with conn() as c:
        return [dict(r) for r in c.execute(
            """SELECT * FROM jobs WHERE score >= ? AND status IN ('ranked','shortlisted')
               ORDER BY score DESC LIMIT ?""", (min_score, limit))]


def add_contact(name, company="", role="", linkedin_url="", email="",
                relationship="employee", job_id=None, notes=""):
    with conn() as c:
        cur = c.execute(
            """INSERT INTO contacts (name, company, role, linkedin_url, email,
               relationship, job_id, notes, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (name, company, role, linkedin_url, email, relationship, job_id,
             notes, _now(), _now()),
        )
        return cur.lastrowid


def find_contact(name):
    with conn() as c:
        r = c.execute(
            "SELECT * FROM contacts WHERE name LIKE ? ORDER BY updated_at DESC",
            (f"%{name}%",)).fetchone()
        return dict(r) if r else None


def set_contact_status(contact_id, status):
    with conn() as c:
        c.execute("UPDATE contacts SET status=?, updated_at=? WHERE id=?",
                  (status, _now(), contact_id))


def log_event(kind, job_id=None, contact_id=None, detail=""):
    with conn() as c:
        c.execute("INSERT INTO events (ts, job_id, contact_id, kind, detail) VALUES (?,?,?,?,?)",
                  (_now(), job_id, contact_id, kind, detail))
    if kind == "applied" and job_id:
        set_status(job_id, "applied")
    if kind == "messaged" and contact_id:
        set_contact_status(contact_id, "messaged")
    if kind == "replied" and contact_id:
        set_contact_status(contact_id, "replied")


def followups_due(after_days=6, max_followups=2):
    """Contacts messaged >= after_days ago with no reply and < max_followups bumps."""
    with conn() as c:
        rows = c.execute("""
            SELECT ct.*,
                   MAX(CASE WHEN e.kind IN ('messaged','followed_up') THEN e.ts END) AS last_touch,
                   SUM(CASE WHEN e.kind='followed_up' THEN 1 ELSE 0 END) AS bumps
            FROM contacts ct JOIN events e ON e.contact_id = ct.id
            WHERE ct.status = 'messaged'
            GROUP BY ct.id
        """).fetchall()
    due = []
    now = datetime.now(timezone.utc)
    for r in rows:
        if r["bumps"] and r["bumps"] >= max_followups:
            continue
        if not r["last_touch"]:
            continue
        last = datetime.strptime(r["last_touch"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if (now - last).days >= after_days:
            due.append(dict(r))
    return due


def counts_today():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with conn() as c:
        row = c.execute("""
            SELECT
              SUM(CASE WHEN kind='applied' THEN 1 ELSE 0 END) AS applied,
              SUM(CASE WHEN kind IN ('messaged','followed_up') THEN 1 ELSE 0 END) AS messaged
            FROM events WHERE ts LIKE ?""", (f"{today}%",)).fetchone()
        return {"applied": row["applied"] or 0, "messaged": row["messaged"] or 0}


def pipeline_snapshot():
    with conn() as c:
        jobs = {r["status"]: r["n"] for r in c.execute(
            "SELECT status, COUNT(*) n FROM jobs GROUP BY status")}
        contacts = {r["status"]: r["n"] for r in c.execute(
            "SELECT status, COUNT(*) n FROM contacts GROUP BY status")}
        return {"jobs": jobs, "contacts": contacts}
