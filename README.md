# job-searcher

A personal, human-in-the-loop job search agent. It finds remote-friendly jobs from
high-signal sources, ranks them against a real profile, tailors application materials,
and drafts warm (non-spammy) outreach messages in the job seeker's own voice.

**It never sends anything by itself.** Every message and application lands in an
`outbox/` folder for review. The human presses send. That's deliberate: it keeps the
outreach honest, keeps LinkedIn from flagging the account, and keeps quality high —
which is what actually gets replies.

## What it does

1. **Discover** — pulls fresh postings from job board APIs (Remotive, RemoteOK,
   WeWorkRemotely, Himalayas) and directly from company career pages (Greenhouse,
   Lever, Ashby public APIs) for a watchlist of target companies. No fragile scraping,
   no ToS problems.
2. **Rank** — an LLM scores every posting 0–100 against `config/profile.yaml`
   (skills, experience, constraints like "remote only", timezone, salary floor) and
   explains the fit. Only the top matches deserve human attention.
3. **Tailor** — for a chosen job, generates tailored resume bullet suggestions and a
   short cover note keyed to the actual posting text.
4. **Outreach** — drafts the messages that actually move the needle: informational
   interview asks to people on the team, a short note to the hiring manager after
   applying, recruiter intros, referral asks, and follow-ups. Built from proven
   templates, rewritten in *her* voice.
5. **Voice** — builds a voice profile from a corpus of her own writing (exported
   emails, messages) so drafts sound like her, not like a language model.
6. **Humanize** — a linter that catches known AI tells (banned words, em dashes,
   "not just X, it's Y" constructions, uniform sentence rhythm, sycophantic openers)
   plus an LLM rewrite pass. Drafts don't reach the outbox until they pass.
7. **Track** — a SQLite pipeline tracker for jobs, contacts, and follow-ups, with a
   daily report of what needs doing.

## Quick start (the easy way: the app)

```bash
pip install -r requirements.txt
python -m agent gui             # opens the web app in your browser
```

**First run opens a guided setup wizard** that walks through everything: pasting a
DeepSeek API key (with a live "does this key work?" test), building the profile with
a friendly form, teaching the app your writing style by pasting a few of your own
messages, and a tour of how to actually run a job search with it. No files to edit.
It can be re-run anytime from the Help page.

Works the same on **Windows** (double-click `run-app.bat`; see `docs/setup-windows.md`
for a from-zero guide), **macOS** (double-click `run-app.command`, or
`python3 -m agent gui`), and **Linux**. The app has buttons for everything below, plus
a drafts inbox with a copy button and an "I sent it ✓" tracker, and a People page for
logging replies and calls. Power users can still configure by hand
(`.env.example` → `.env`, `config/profile.example.yaml` → `config/profile.yaml`).

## Quick start (the CLI way)

```bash
# build her voice profile from her own writing (see voice/corpus/README.md)
python -m agent voice-build

# daily loop
python -m agent discover        # pull fresh jobs
python -m agent rank            # score them against the profile
python -m agent report          # what's worth applying to + follow-ups due
python -m agent tailor --job <id>
python -m agent outreach --job <id> --kind info_interview --person "Jane Doe" --person-role "Data Analyst"
```

Set `MOCK_LLM=1` to try the whole pipeline with no API key (canned model replies).

Everything drafted lands in `outbox/` as markdown files with a checklist. Review,
edit if needed, copy into LinkedIn/email, send, then log it:

```bash
python -m agent log --job <id> --event applied
python -m agent log --contact "Jane Doe" --event messaged
```

## Piloting with Claude Code

Open this repo in Claude Code and use the slash commands in `.claude/commands/`:
`/daily-run`, `/triage`, `/draft-outreach`, `/weekly-review`. `CLAUDE.md` teaches the
agent the strategy and the guardrails. No API key needed in that mode — Claude Code
is the LLM.

## Piloting with DeepSeek

Set `DEEPSEEK_API_KEY` in `.env`. The client speaks the OpenAI-compatible API at
`https://api.deepseek.com` (model `deepseek-v4-flash` by default; set
`DEEPSEEK_MODEL=deepseek-v4-pro` for higher-quality drafts). A full week of heavy
use (hundreds of rankings, dozens of drafts) costs well under a dollar — and
DeepSeek caches identical prompt prefixes automatically, so repeated ranking runs
bill most input at the ~98%-discounted cache-hit rate. The prompts in this repo
are already ordered stable-prefix-first to exploit that.

## The strategy (short version)

The research behind this is in `docs/research/`. The distilled playbook is
`docs/playbook.md`. The one-paragraph version:

Mass auto-apply is a lottery with bad odds and it's getting worse — employers are
drowning in AI slop and filtering harder. What works is the opposite: a focused list
of target companies, 10–20 genuinely tailored applications a week, and *people* —
2–5 warm, specific messages a day to employees, hiring managers, and recruiters at
those companies. Referred candidates get interviewed at many times the rate of cold
applicants. This system automates the grunt work (finding, filtering, drafting,
remembering to follow up) so the human hour a day goes entirely into the part that
works: real conversations.

## Ethics & safety rails

- Human sends every message. No LinkedIn automation, no bot clicks.
- Volume caps in `config/settings.yaml` (default: ≤5 new outreach/day, ≤15
  connection requests/week) — far under platform limits, and more importantly,
  consistent with quality.
- The voice corpus must be **her** writing, provided by her. Don't feed it other
  people's emails.
- Drafts are starting points. The rule: never send a message you wouldn't be happy
  to defend as your own words.
