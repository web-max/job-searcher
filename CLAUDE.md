# CLAUDE.md — piloting this repo

This is a human-in-the-loop job search agent for one person. Read
`docs/playbook.md` for the strategy; `docs/research/` has the evidence.

## Prime directives

1. **Never send anything.** Messages, applications, connection requests — all of it is
   drafted into `outbox/` and a human sends it. Never automate a logged-in browser
   action on LinkedIn or any job platform. This is non-negotiable: it's a ban risk for
   her accounts and it's the difference between outreach and spam.
2. **Never fabricate.** No invented experience, metrics, or mutual connections in any
   draft. If the profile doesn't support a claim, don't make it.
3. **Respect the volume caps** in `config/settings.yaml`. If today's cap is reached,
   queue drafts for tomorrow instead.
4. **Her voice, not yours.** Every draft must pass through the voice profile
   (`voice/voice_profile.md`) and the linter (`agent/humanize.py`). If
   `python -m agent lint` flags high-severity tells, fix them before presenting.
5. **Privacy.** `config/profile.yaml`, `voice/`, `data/`, and `outbox/` are gitignored
   personal data. Never commit them, never paste their contents into PRs or issues.

## How to run things

```bash
python -m agent discover      # pull fresh jobs (APIs only, no scraping)
python -m agent rank          # LLM-score against config/profile.yaml
python -m agent report        # top matches + follow-ups due + pipeline
python -m agent tailor --job <id>
python -m agent outreach --kind info_interview --person "Name" --person-role "Role" --company "Co" --job <id> --context "specific detail about them"
python -m agent voice-build   # rebuild voice profile from voice/corpus/
python -m agent lint --file outbox/some-draft.md
python -m agent log --job <id> --event applied
```

When you (Claude Code) are the pilot, you can do the LLM steps yourself instead of
calling the API: read the unranked jobs from the tracker (`data/tracker.db`, table
`jobs`), score them with the rubric in `agent/rank.py`'s SYSTEM prompt, and write
scores back with `agent.tracker.set_score`. Same for drafting: follow
`agent/outreach.py`'s SYSTEM prompt + the matching template in `templates/outreach/`
+ the voice profile, then lint with `python -m agent lint`.

## Drafting rules (summary of docs/research/05-ai-writing-tells.md)

- First sentence: a specific, true detail about the recipient/company. The "swap
  test": if the message would still make sense sent to someone else, it's too generic.
- One ask per message, as a question, with a concrete CTA. >50% of words about them.
- LinkedIn note ≤300 chars; DM ≤110 words; email ≤130 words; cover note ≤260 words.
- No em dashes. No "not just X, it's Y". Max one A-B-and-C triad. No "-ing" analysis
  tails. No flattery openers, no "I hope this finds you well", no summary closers.
  Vary sentence lengths. Use her greeting/sign-off habits from the voice profile.
- The banned/flag word lists are in `agent/tells.py`; her personal whitelist
  (`voice/whitelist.json`) overrides them.

## What to do on a typical "daily run" request

1. discover → rank → report.
2. Present the top 3–5 jobs with scores and one-line reasons. Ask which to tailor.
3. For each chosen job: tailor kit, then propose the outreach trio (employee /
   recruiter / hiring manager) and draft what she approves.
4. Surface follow-ups due, draft bumps for the ones she confirms.
5. Remind her of today's counts vs caps. Stop at the caps.
