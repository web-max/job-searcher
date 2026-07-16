"""Tailor application materials for a specific job: keyword-gap analysis,
resume bullet suggestions, and a short cover note - never fabricating anything.
"""
from datetime import datetime, timezone

from . import humanize, llm, tracker, voice
from .paths import OUTBOX_DIR
from .settings import load_profile, profile_summary_for_llm

SYSTEM = """You are a careful application coach. You get a candidate profile and one
job posting. Produce three sections in markdown:

## Keyword gaps
Terms from the posting that a recruiter would search for, split into:
- COVERED: terms her background genuinely supports (say which experience covers each)
- MISSING-BUT-TRUE: things she has done but should state explicitly
- MISSING-AND-NOT-TRUE: requirements she does not meet. Never suggest faking these;
  note if any is a likely knockout question (visa, location, license, years).

## Resume bullet suggestions
3-6 rewritten bullets using HER real experience, reworded toward this posting's
language. Every claim must trace to the profile. No invented metrics - where a metric
would help, write [her real number] for her to fill in.

## Cover note
A short note (under 180 words) in her voice: why this company specifically (from the
posting), the 2 strongest true matches, one concrete proof point, and a plain closing.
No "I am writing to express", no flattery, no summary closer.

Honesty rule: fabricated claims get candidates blacklisted. If the fit is weak, say so
at the top and suggest whether it's worth applying."""


def run(job_id: str) -> str:
    job = tracker.get_job(job_id)
    if not job:
        raise SystemExit(f"job {job_id} not found; run discover/rank first")
    profile = load_profile()
    vp = voice.get_profile()

    user = f"""CANDIDATE:
{profile_summary_for_llm(profile)}

VOICE PROFILE (for the cover note):
{vp}

JOB POSTING:
company: {job['company']}
title: {job['title']}
location: {job['location']}
url: {job['url']}
description:
{job['description'][:4500]}"""

    result = llm.complete(SYSTEM, user, max_tokens=2000, temperature=0.5)

    # lint just the cover note portion
    note = result.split("## Cover note", 1)[-1]
    findings = humanize.lint(note, kind="cover_note")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    fname = OUTBOX_DIR / f"{ts}-tailor-{job['id']}.md"
    fname.write_text(f"""# Application kit: {job['title']} @ {job['company']}

- url: {job['url']}
- score: {job.get('score')} ({job.get('score_reason', '')})

{result}

## Linter findings on the cover note
{humanize.format_findings(findings)}

## Before applying
- [ ] Fill in any [her real number] placeholders with true numbers
- [ ] Verify every claim is true - nothing invented survives an interview
- [ ] Apply on the company's own careers page, not Easy Apply, when possible
- [ ] Then log it: python -m agent log --job {job['id']} --event applied
- [ ] Same day: find 1 employee + the recruiter, draft outreach (see /draft-outreach)
""")
    tracker.set_status(job_id, "shortlisted")
    print(f"application kit written to {fname}")
    return str(fname)
