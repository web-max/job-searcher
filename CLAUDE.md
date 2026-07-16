# CLAUDE.md — piloting this repo

This is a human-in-the-loop job search agent for one person. Read
`docs/playbook.md` for the strategy; `docs/research/` has the evidence.

## Prime directives

1. **Never submit anything.** Messages, applications, connection requests — a human
   presses every send/submit button. Machines may do all the mechanical prep up to
   that button: assisted apply (`python -m agent apply --job <id>`, off by default,
   toggled in settings) fills non-LinkedIn ATS forms and stops on the filled form for
   her review. Two hard sub-rules: **LinkedIn is never automated** in any way (account
   ban risk), and **EEO/demographic/salary questions are never machine-answered.**
2. **Never fabricate.** No invented experience, metrics, or mutual connections in any
   draft. If the profile doesn't support a claim, don't make it.
3. **Respect the volume caps** in `config/settings.yaml`. If today's cap is reached,
   queue drafts for tomorrow instead.
4. **Her voice, not yours.** Every draft must pass through the voice profile
   (`voice/voice_profile.md`) and the linter (`agent/humanize.py`). If
   `python -m agent lint` flags high-severity tells, fix them before presenting.
5. **Privacy.** `config/profile.yaml`, `voice/`, `data/`, and `outbox/` are gitignored
   personal data. Never commit them, never paste their contents into PRs or issues.

## Human intelligence in the loop, not a human meat puppet (owner decision, 2026-07-16)

The human-in-the-loop check exists for judgment, not for labor. Reviewing a filled
form, catching a claim that isn't true, deciding "this sounds like me", pressing
submit — that is human intelligence, and it stays human. Copy-pasting machine output
field by field into a form is meat-puppet work: the machine already did the thinking
and the human is just its hands. Automate the meat-puppet part; never the judgment
part.

The practical line: machines may draft, fill, and prepare everything right up to the
submit/send button, and must always land the human on a reviewable screen where every
machine-entered value can be checked and corrected before she fires. That's why
assisted apply exists, why it never clicks submit, and why the LinkedIn and
EEO/demographic exclusions above are hard limits rather than defaults.

## How to run things

```bash
python -m agent discover      # pull fresh jobs (APIs only, no scraping)
python -m agent rank          # LLM-score against config/profile.yaml
python -m agent report        # top matches + follow-ups due + pipeline
python -m agent tailor --job <id>
python -m agent apply --job <id>   # fill the ATS form locally, stop for review; needs apply.form_autofill on
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
