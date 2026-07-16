Triage the current job pipeline:

1. `python -m agent report`.
2. For each top match, sanity-check the score: read the job row in data/tracker.db and flag scoring mistakes (location conflicts, seniority mismatches, scam signals per docs/playbook.md's scam filter).
3. Mark obvious mistakes: `python -m agent status --job <id> --to dropped`.
4. Recommend the 1-3 jobs most worth applying to today and say why in one sentence each.
