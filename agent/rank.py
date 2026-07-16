"""LLM ranking of discovered jobs against the profile."""
import json

from . import llm, tracker
from .settings import profile_summary_for_llm

SYSTEM = """You are a picky, experienced career coach screening job postings for one
specific candidate. You are allergic to wishful thinking: a posting only scores high
if the candidate would plausibly get an interview. Score each job 0-100:
  90+: unusually strong fit, apply today
  75-89: solid fit, worth a tailored application
  65-74: plausible stretch, apply if the week's quota allows
  <65: skip (wrong seniority, wrong field, location conflict, dealbreaker)
Location is a KNOCKOUT, not a preference: if the posting restricts hiring to
countries or regions that do not include the candidate's country of residence
(e.g. "USA only", "must be US-based", "EU work authorization required" for a
non-EU candidate), score it below 40 no matter how good the skills fit is -
payroll and residency requirements are non-negotiable. "Worldwide", "anywhere",
the candidate's own country/region, or silence about location are all fine.
Penalize hard: timezone conflicts with the candidate's constraints, seniority
mismatch by more than one level, required skills the candidate clearly lacks.
Reward: overlap with the candidate's strongest experience, explicit remote
friendliness, region-inclusive hiring (worldwide / the candidate's region /
"hire through Deel/Remote/Oyster" style employer-of-record language), salary at
or above the floor, and timezone alignment stated as an asset."""


def rank_batch(profile_text: str, jobs: list) -> list:
    listing = []
    for j in jobs:
        listing.append(
            f"JOB {j['id']}\ncompany: {j['company']}\ntitle: {j['title']}\n"
            f"location: {j['location']}\nsalary: {j['salary']}\n"
            f"description: {j['description'][:1500]}\n"
        )
    user = (
        f"CANDIDATE:\n{profile_text}\n\nJOBS:\n" + "\n---\n".join(listing) +
        '\n\nReturn JSON: {"scores": [{"id": "<job id>", "score": <int>, '
        '"reason": "<one concrete sentence>"}]} — one entry per job, every job scored.'
    )
    data = llm.complete_json(SYSTEM, user, max_tokens=4000)
    return data.get("scores", [])


def run(profile: dict, settings: dict) -> dict:
    jobs = tracker.unranked_jobs()
    if not jobs:
        return {"ranked": 0, "surfaced": 0}
    profile_text = profile_summary_for_llm(profile)
    batch_size = settings.get("ranking", {}).get("batch_size", 12)
    min_score = settings.get("ranking", {}).get("min_score_to_surface", 65)

    ranked = surfaced = 0
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i + batch_size]
        try:
            scores = rank_batch(profile_text, batch)
        except llm.LLMError as e:
            print(f"  ranking batch failed: {e}")
            continue
        by_id = {s.get("id"): s for s in scores if isinstance(s, dict)}
        for j in batch:
            s = by_id.get(j["id"])
            if not s:
                continue
            score = int(s.get("score", 0))
            tracker.set_score(j["id"], score, s.get("reason", ""))
            ranked += 1
            if score >= min_score:
                surfaced += 1
        print(f"  ranked {min(i + batch_size, len(jobs))}/{len(jobs)}")
    return {"ranked": ranked, "surfaced": surfaced}
