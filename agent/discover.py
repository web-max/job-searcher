"""Job discovery from stable, public, ToS-friendly sources.

Sources (all official APIs or feeds — nothing that scrapes a logged-in site):
  - Remotive:        https://remotive.com/api/remote-jobs?search=<term>
  - RemoteOK:        https://remoteok.com/api
  - WeWorkRemotely:  https://weworkremotely.com/remote-jobs.rss
  - Himalayas:       https://himalayas.app/jobs/api
  - Greenhouse:      https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true
  - Lever:           https://api.lever.co/v0/postings/<slug>?mode=json
  - Ashby:           https://api.ashbyhq.com/posting-api/job-board/<slug>
  - HN Who's Hiring: Algolia API (optional, tech-heavy)

Every job is normalized to a dict and upserted into the tracker DB keyed by a
stable hash of (source, url), so re-running discover is idempotent.
"""
import hashlib
import html
import re
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

from . import tracker

UA = {"User-Agent": "job-searcher personal agent (contact: owner of this repo)"}


def _get(url: str, **kw):
    try:
        resp = requests.get(url, headers=UA, timeout=30, **kw)
        if resp.status_code == 200:
            return resp
        print(f"  warn: {url} -> HTTP {resp.status_code}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"  warn: {url} -> {e}", file=sys.stderr)
    return None


def _strip_html(text: str) -> str:
    # unescape BEFORE stripping (twice, for double-escaped payloads like
    # Greenhouse's &lt;div&gt; content), otherwise escaped tags survive the regex
    # and get unescaped into literal markup afterwards
    text = html.unescape(html.unescape(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _fix_mojibake(text: str) -> str:
    """Repair double-encoded UTF-8 from sloppy sources ('SÃ£o Paulo' -> 'São Paulo')."""
    if "Ã" in text or "â€" in text:
        try:
            repaired = text.encode("latin-1").decode("utf-8")
            if "Ã" not in repaired:
                return repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text


def _job(source, company, title, url, location="", description="", posted_at="", salary=""):
    jid = hashlib.sha1(f"{source}|{url}".encode()).hexdigest()[:12]
    return {
        "id": jid,
        "source": source,
        "company": _fix_mojibake((company or "").strip()),
        "title": _fix_mojibake((title or "").strip()),
        "url": url,
        "location": _fix_mojibake((location or "").strip()),
        "description": _fix_mojibake(_strip_html(description)[:6000]),
        "posted_at": posted_at or "",
        "salary": salary or "",
    }


def _matches_terms(text: str, terms: list) -> bool:
    if not terms:
        return True
    lowered = text.lower()
    return any(t.lower() in lowered for t in terms)


# ---------------------------------------------------------------- sources

def fetch_remotive(terms):
    jobs = []
    for term in terms or [""]:
        resp = _get("https://remotive.com/api/remote-jobs", params={"search": term, "limit": 100})
        if not resp:
            continue
        for j in resp.json().get("jobs", []):
            jobs.append(_job(
                "remotive", j.get("company_name"), j.get("title"), j.get("url"),
                location=j.get("candidate_required_location", ""),
                description=j.get("description", ""),
                posted_at=(j.get("publication_date") or "")[:10],
                salary=j.get("salary", ""),
            ))
        time.sleep(1)
    return jobs


def fetch_remoteok(terms):
    resp = _get("https://remoteok.com/api")
    if not resp:
        return []
    jobs = []
    for j in resp.json():
        if not isinstance(j, dict) or not j.get("position"):
            continue
        blob = f"{j.get('position','')} {' '.join(j.get('tags') or [])} {j.get('description','')}"
        if not _matches_terms(blob, terms):
            continue
        salary = ""
        if j.get("salary_min") and j.get("salary_max"):
            salary = f"${j['salary_min']}-${j['salary_max']}"
        jobs.append(_job(
            "remoteok", j.get("company"), j.get("position"),
            j.get("url") or f"https://remoteok.com/remote-jobs/{j.get('id')}",
            location=j.get("location", "Remote"),
            description=j.get("description", ""),
            posted_at=(j.get("date") or "")[:10],
            salary=salary,
        ))
    return jobs


def fetch_weworkremotely(terms):
    """Parse the WWR RSS feed with the stdlib (feedparser's sgmllib3k dependency
    fails to build on some systems, and plain RSS doesn't need it)."""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime

    resp = _get("https://weworkremotely.com/remote-jobs.rss")
    if not resp:
        return []
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        print(f"  warn: WWR RSS parse failed: {e}", file=sys.stderr)
        return []
    jobs = []
    for item in root.iter("item"):
        def field(tag):
            el = item.find(tag)
            return (el.text or "") if el is not None else ""
        title = field("title")  # format: "Company: Job Title"
        company, _, role = title.partition(":")
        summary = field("description")
        if not _matches_terms(f"{title} {summary}", terms):
            continue
        posted = ""
        if field("pubDate"):
            try:
                posted = parsedate_to_datetime(field("pubDate")).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                posted = ""
        region = field("{https://weworkremotely.com}region") or field("region") or "Remote"
        jobs.append(_job(
            "weworkremotely", company, role.strip() or title, field("link"),
            location=region, description=summary, posted_at=posted,
        ))
    return jobs


def fetch_himalayas(terms, pages=10):
    """API returns max 20 jobs per request; walk a few pages of the newest postings."""
    raw = []
    for page in range(pages):
        resp = _get("https://himalayas.app/jobs/api", params={"limit": 20, "offset": page * 20})
        if not resp:
            break
        batch = resp.json().get("jobs", [])
        raw.extend(batch)
        if len(batch) < 20:
            break
        time.sleep(0.5)
    jobs = []
    for j in raw:
        desc = j.get("description") or j.get("excerpt") or ""
        blob = f"{j.get('title','')} {' '.join(j.get('categories') or [])} {desc}"
        if not _matches_terms(blob, terms):
            continue
        posted = ""
        if j.get("pubDate"):
            try:
                posted = datetime.fromtimestamp(int(j["pubDate"]), tz=timezone.utc).strftime("%Y-%m-%d")
            except (ValueError, TypeError, OSError):
                posted = ""
        salary = ""
        if j.get("minSalary") and j.get("maxSalary"):
            salary = f"{j.get('currency','')} {j['minSalary']}-{j['maxSalary']}".strip()
        company = j.get("companyName")
        if isinstance(company, dict):
            company = company.get("name", "")
        if not company or str(company).strip().lower() == "name":
            # field occasionally comes through junk; recover from the slug
            company = (j.get("companySlug") or "").replace("-", " ").title()
        jobs.append(_job(
            "himalayas", company, j.get("title"),
            j.get("applicationLink") or j.get("guid", ""),
            location=", ".join(j.get("locationRestrictions") or []) or "Remote",
            description=desc,
            posted_at=posted,
            salary=salary,
        ))
    return jobs


def fetch_watchlist(watchlist):
    """Poll target companies' career pages via their public board APIs."""
    jobs = []
    for entry in watchlist or []:
        name, board, slug = entry.get("name"), entry.get("board"), entry.get("slug")
        if not (board and slug):
            continue
        if board == "greenhouse":
            resp = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", params={"content": "true"})
            if resp:
                for j in resp.json().get("jobs", []):
                    jobs.append(_job(
                        "watchlist:greenhouse", name, j.get("title"), j.get("absolute_url"),
                        location=(j.get("location") or {}).get("name", ""),
                        description=j.get("content", ""),
                        posted_at=(j.get("updated_at") or "")[:10],
                    ))
        elif board == "lever":
            resp = _get(f"https://api.lever.co/v0/postings/{slug}", params={"mode": "json"})
            if resp:
                for j in resp.json():
                    jobs.append(_job(
                        "watchlist:lever", name, j.get("text"), j.get("hostedUrl"),
                        location=(j.get("categories") or {}).get("location", ""),
                        description=j.get("descriptionPlain", ""),
                        posted_at=datetime.fromtimestamp(
                            (j.get("createdAt") or 0) / 1000, tz=timezone.utc
                        ).strftime("%Y-%m-%d") if j.get("createdAt") else "",
                    ))
        elif board == "ashby":
            resp = _get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", params={"includeCompensation": "true"})
            if resp:
                for j in resp.json().get("jobs", []):
                    jobs.append(_job(
                        "watchlist:ashby", name, j.get("title"), j.get("jobUrl") or j.get("applyUrl"),
                        location=j.get("location", ""),
                        description=j.get("descriptionPlain") or "",
                        posted_at=(j.get("publishedAt") or "")[:10],
                    ))
        time.sleep(1)
    return jobs


def fetch_hn_whoishiring(terms):
    """Latest 'Ask HN: Who is hiring?' thread via the Algolia API.

    The author_whoishiring tag is essential - a bare story search fuzzily
    matches unrelated Ask HN posts."""
    resp = _get(
        "https://hn.algolia.com/api/v1/search_by_date",
        params={"query": "Ask HN: Who is hiring?",
                "tags": "story,author_whoishiring", "hitsPerPage": 1},
    )
    if not resp or not resp.json().get("hits"):
        return []
    story = resp.json()["hits"][0]
    if not (story.get("title") or "").startswith("Ask HN: Who is hiring?"):
        return []
    resp = _get(f"https://hn.algolia.com/api/v1/items/{story['objectID']}")
    if not resp:
        return []
    jobs = []
    for c in resp.json().get("children", []):
        text = _strip_html(c.get("text") or "")
        if len(text) < 60 or not _matches_terms(text, terms):
            continue
        # convention: "Company | Role | Location | ..." on the first line
        first_line = text.splitlines()[0] if "\n" in text else text
        parts = [p.strip() for p in first_line.split("|")]
        company = parts[0].split(".")[0][:60]
        title = (parts[1] if len(parts) > 1 else first_line.split(".")[0])[:120]
        jobs.append(_job(
            "hn_whoishiring", company, title,
            f"https://news.ycombinator.com/item?id={c['id']}",
            location=parts[2][:80] if len(parts) > 2 else "see post",
            description=text,
            posted_at=(c.get("created_at") or "")[:10],
        ))
    return jobs


# ---------------------------------------------------------------- main

def run(profile: dict, settings: dict) -> dict:
    terms = profile.get("search_terms") or profile.get("target_titles") or []
    src_cfg = settings.get("discovery", {}).get("sources", {})
    max_age = settings.get("discovery", {}).get("max_age_days", 21)

    fetchers = [
        ("remotive", lambda: fetch_remotive(terms)),
        ("remoteok", lambda: fetch_remoteok(terms)),
        ("weworkremotely", lambda: fetch_weworkremotely(terms)),
        ("himalayas", lambda: fetch_himalayas(terms)),
        ("watchlist_boards", lambda: fetch_watchlist(profile.get("watchlist"))),
        ("hn_who_is_hiring", lambda: fetch_hn_whoishiring(terms)),
    ]

    all_jobs, per_source = [], {}
    for key, fn in fetchers:
        if not src_cfg.get(key, False):
            continue
        print(f"fetching {key} ...")
        found = fn()
        per_source[key] = len(found)
        all_jobs.extend(found)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age)).strftime("%Y-%m-%d")
    fresh = [j for j in all_jobs if not j["posted_at"] or j["posted_at"] >= cutoff]

    dealbreakers = [d.lower() for d in profile.get("dealbreakers") or []]
    kept = [
        j for j in fresh
        if not any(d in (j["title"] + " " + j["description"]).lower() for d in dealbreakers)
    ]

    new_count = tracker.upsert_jobs(kept)
    return {"fetched": len(all_jobs), "fresh": len(fresh), "kept": len(kept),
            "new": new_count, "per_source": per_source}
