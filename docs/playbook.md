# The Playbook

Everything below is distilled from the five research reports in `docs/research/`.
Numbers cited there. This is the strategy the system is built around.

## Why the obvious approach fails

Mass applying is the default instinct and it's the worst play in 2026. Applications
are up 45%+ year over year, single remote roles pull 1,000+ applicants, and employers
now run bot detection, AI-content screening, and cross-company fraud lists. Baseline
cold-application results: 2–5% response, ~3% reach interview, 75% get no response at
all. Auto-apply tools do worse (one documented run: 47 applications, 0 interviews),
and LinkedIn permanently bans accounts for automation.

Meanwhile referred candidates reach interviews at ~40% and get hired at 4–9x the
cold-application rate — and referrals are under 1% of application volume, so the lane
is empty. The market punishes volume and pays for warmth. That's the whole game.

## The weekly operating system (~1 focused hour a day)

**One-time setup (weekend 1)**
1. Fill in `config/profile.yaml` honestly. Add a watchlist of 20–40 target companies
   (Dalton's LAMP method: score companies by how much she actually wants to work
   there, not by whether they have a posting today).
2. Export her sent mail, run `python -m agent voice-build`.
3. LinkedIn hygiene: Open to Work (recruiters-only is fine), up to 5 target titles,
   "Remote" job type PLUS several acceptable metros (recruiters search by metro even
   for remote roles), remote keywords in the headline, "(Remote)" labels on past roles.
4. Resume: honest keyword coverage for her target titles. There is no keyword
   auto-rejector in Greenhouse/Lever — humans read applications. Keywords matter
   because recruiters *search* the database; missing ones make her invisible, not
   rejected. The only hard machine gate is knockout questions.

**Daily (Mon–Fri)**
1. `python -m agent discover && python -m agent rank && python -m agent report` (5 min)
2. Apply to 1–3 jobs scoring 75+, each within 24–72h of posting, each with
   `python -m agent tailor --job <id>` output reviewed and personalized (30 min).
   Apply on the company careers page, not Easy Apply.
3. The needle-mover: 2–5 outreach messages (20 min). For each job applied to, same day:
   - one peer-level employee (alum if possible) → informational ask
   - the recruiter on the req → short intro naming the req
   - optionally the hiring manager → short fit note
   Send Tue–Thu business hours in their timezone. She sends every message herself.
4. Log everything: `python -m agent log ...`. Follow-ups surface automatically.

**Weekly**
- 10–20 tailored applications total, max. More is spray.
- ≤15–20 connection requests/day, well under the ~100/week ceiling; keep acceptance
  above 30–40%; withdraw invites pending >3 weeks.
- Review the pipeline: what got replies? Double down on that channel.

**Per conversation that lands**
- 15-minute call → TIARA arc (their trends, insights, advice, resources, assignments).
- Thank-you within 24h naming one thing she learned and one action taken.
- Do the thing they suggested; report back in 1–2 weeks. That loop converts advisers
  into advocates — the referral usually offers itself at this point. If not:
  "would you feel comfortable referring me?" with an explicit out.

## Rules that protect her

- **She sends everything.** The system drafts; a human presses send. This is what keeps
  her account safe, her reputation clean, and the messages good.
- **Never fabricate.** No invented metrics, skills, or mutual connections. Fabrications
  now land in cross-company fraud databases.
- **Never pitch a stranger.** First message asks about *their* experience. Referral asks
  come only after a real interaction.
- **One bump max on LinkedIn**, two on email, then let go gracefully.
- **Scam filter** for remote listings: no SMS/WhatsApp/Telegram recruiting, no
  free-mail recruiter addresses, no chat-only interviews, no pre-offer payments or
  bank details, verify the posting exists on the company's own careers page.
  greenhouse.io / lever.co / ashbyhq.com application URLs are a good sign.

## Where the leverage actually is

| Activity | Automatable? | Payoff |
|---|---|---|
| Finding fresh, real postings | Fully (this repo) | High — freshness beats volume |
| Filtering/ranking | Fully (this repo) | High — protects her attention |
| Keyword-gap analysis + tailoring | Draft-only | High — 3–5x response vs generic |
| Outreach drafting in her voice | Draft-only | Highest — referral path |
| Sending | **Never** | The human touch IS the product |
| Follow-up memory | Fully (this repo) | High — 42% of replies come from follow-ups |
| Interview prep | Chat/voice with any LLM | High, free |

## Morale notes (for the human running this)

The median successful search in this market is ~6 months and ~30+ applications even
done well. Build for a marathon: small daily quota, visible pipeline progress
(`python -m agent report` shows motion even on quiet days), and celebrate replies and
calls as wins — they're the leading indicators, offers are the lagging one.
Never Search Alone's peer "Job Search Councils" (phyl.org, free) exist precisely
because solo searching grinds people down. Worth joining one.
