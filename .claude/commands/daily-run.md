Run the daily job search loop as described in CLAUDE.md:

1. `python -m agent discover` then `python -m agent rank` (if no API key is set, do the ranking yourself: read unranked jobs from data/tracker.db, score each 0-100 against config/profile.yaml using the rubric in agent/rank.py, write back via agent.tracker.set_score).
2. `python -m agent report` and present the top matches with one-line reasons.
3. Ask which jobs to tailor, then run tailor for each and summarize the kits.
4. For each tailored job, propose the outreach trio (peer employee, recruiter, hiring manager) with what research is still needed (their names, a specific detail). Draft the ones approved.
5. List follow-ups due and draft approved bumps.
6. Close with today's counts vs the volume caps in config/settings.yaml.

Never send anything. Everything lands in outbox/ for human review.
