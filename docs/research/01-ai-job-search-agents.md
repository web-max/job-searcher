# How People Are Using AI Agents & LLMs to Find Jobs (2025–2026 Research Report)

## 1. Real techniques people report using

**AI-tailored resumes per posting (most common, most endorsed)**
- ~1 in 3 job seekers now use AI in their search; the standard workflow reported on Reddit/blogs: paste job description + master resume into ChatGPT/Claude → ask for keyword gap analysis and rewritten bullets → human-edit before sending ([Interview Guys State of Job Search 2025](https://blog.theinterviewguys.com/state-of-job-search-2025-research-report/), [Slate on the "AI black hole"](https://slate.com/technology/2025/10/job-search-artificial-intelligence-chatgpt-resume-cover-letter.html)).
- The failure mode users repeatedly report: LLMs hallucinate metrics and invent skills. Hiring managers on the [AIHawk HN thread](https://news.ycombinator.com/item?id=41756371) reported catching AI resumes claiming technologies candidates had never used — candidates often didn't know their own resume said it.

**Personal scraping + LLM-ranking pipelines (the builder crowd's approach)**
- A visible 2025–2026 pattern: engineers building "morning job digest" agents — scrape boards → LLM scores each posting 1–10 against your CV/criteria → ranked list delivered daily. Examples: [Claude + GitHub Actions + Notion pipeline](https://dev.to/ozfarooq/how-i-built-a-job-finder-agent-with-claude-ai-github-actions-and-notion-e9c) (fetch → score → store, zero hosting), [5am job-finder agent](https://genaiunplugged.substack.com/p/ai-job-finder-agent-claude-code), and a [multi-agent Claude Code system with 631 evaluations and 10-dimensional scoring + dedup against 680 URLs](https://dev.to/santifer/i-built-a-multi-agent-job-search-system-with-claude-code-631-evaluations-12-modes-2cd0). Playwright is the standard choice for JS-rendered/login-gated pages.
- Best documented end-to-end result: [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) (Claude Code framework: evaluate postings, tailor CVs, write cover letters, prep interviews) — author reports **69 tailored applications → 20 first interviews (29% conversion)** → hired as AI engineer June 2026. Note: high-touch tailoring, not auto-apply.

**Auto-apply agents (widely tried, widely regretted)**
- [404 Media documented AIHawk applying to 17 jobs in one hour](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/), headline user applied to 2,843 roles. A Reddit user pushed LazyApply past **14,000 applications → mass rejections and ATS spam-flagging** ([LoopCV blog](https://blog.loopcv.pro/what-happened-to-sonara/)).
- HN users on the AIHawk thread rationalized it: ~30 min/manual application at <1% success makes automation feel forced; also framed as "tragedy of the commons."

**Interview prep agents**
- ChatGPT Voice mock interviews are the mainstream free technique — realistic Q&A + feedback, replacing paid coaches ([Tom's Guide first-person account, landed the job](https://www.tomsguide.com/ai/i-used-chatgpt-voice-to-prep-for-a-job-interview-and-it-seriously-reduced-my-anxiety)).
- Live "interview copilots" (Final Round AI, Interview Coder, Sensei) that whisper answers during real interviews exist and sell well but carry detection/ethics risk (see §3).

**AI-drafted cover letters and outreach**
- Standard and accepted *when personalized*: 63% of recruiters accept AI-assisted letters if personalized; 80% reject generic output ([CoverLetterCopilot recruiter data](https://coverlettercopilot.ai/blog/recruiters-human-vs-ai-cover-letters), [Resume Now survey](https://www.resume-now.com/job-resources/careers/ai-applicant-report)).
- Gray-hat: "prompt injection resume hacking" — hidden white-text instructions to AI screeners. Employers now blacklist for it: Manpower detects ~10,000 AI-injected resumes/year (~10% of submissions) and shares flagged-candidate databases across firms ([Forbes](https://www.forbes.com/sites/carolinecastrillon/2025/10/12/how-ai-resume-hacks-are-helping-job-seekers-land-interviews/)).

## 2. Open-source projects and reputations

| Project | Status / reputation |
|---|---|
| [feder-cr/Jobs_Applier_AI_Agent_AIHawk](https://github.com/feder-cr/Jobs_Applier_AI_Agent_AIHawk) | ~30k stars, 4.6k forks — the flagship auto-apply project. **Archived May 17, 2026, now read-only.** Long buggy-beta reputation; HN thread is largely negative from the hiring side. Team pivoted commercial (laboro). Many stale forks circulate. |
| [speedyapply/JobSpy](https://github.com/speedyapply/JobSpy) | ~3.4k+ stars, MIT, actively maintained, `pip install python-jobspy`. **The default scraping building block**: LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter, Bayt → one pandas DataFrame. Indeed scraper is most reliable (no rate limiting); LinkedIn rate-limits ~page 10 per IP, proxies effectively required. TypeScript port exists ([ts-jobspy](https://github.com/alpharomercoma/ts-jobspy)). |
| [srbhr/Resume-Matcher](https://github.com/srbhr/resume-matcher) | Most popular OSS resume-tailoring tool (multi-thousand stars, active): JD + resume → match score, keyword gaps, tailored resume/cover letter, PDF export; supports 100+ LLMs incl. local. |
| [GodsScion/Auto_job_applier_linkedIn](https://github.com/GodsScion/Auto_job_applier_linkedIn) | Active LinkedIn Easy-Apply bot; same ban-risk class as AIHawk. |
| [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | Newer (late 2025) "fork it and own it" Claude Code framework — evaluation/tailoring/prep rather than auto-submit; the architecture most aligned with what actually worked. |

**Ban risk (LinkedIn bots specifically):** LinkedIn is enforcing hard in 2025–2026 — detection of "human-impossible application velocity" (100+ apps/hour), fingerprinting of known automation extensions, account restrictions and permanent bans; Apollo.io and Seamless.ai were banned platform-wide in 2025 ([JobApplyAI legal guide](https://jobapplyai.in/blog/is-auto-applying-linkedin-jobs-against-tos/), [Cleverly](https://www.cleverly.co/blog/why-linkedin-automation-tools-get-your-account-banned-and-what-to-do-instead)). Scraping (read-only, via JobSpy + proxies) is far lower personal risk than automating logged-in applies.

## 3. Commercial tools — what users actually report

- **Simplify (Copilot)** — best-reputation tool in the category: free autofill extension, 1M+ installs, 4.9/5 Chrome store; cuts 15–25 min applications to 1–2 min. It's autofill + tracking, *not* auto-apply. Paid Simplify+ ($39.99/mo) widely called not worth it — no trial, no refund policy, generic AI output ([Remote Job Assistant review](https://www.remotejobassistant.com/blog/simplify-jobs-review)).
- **LazyApply** ($99–249 lifetime) — worst reputation: low Trustpilot, fails to fill basic fields (even names), applies to irrelevant roles, wrong visa answers; systemic refund non-delivery despite "30-day policy." Test run: 47 applications → 0 interviews ([FastApply review](https://blog.fastapply.co/is-lazyapply-legit-2026-review), [Trustpilot](https://www.trustpilot.com/review/lazyapply.com)).
- **Sonara** — cautionary tale: shut down abruptly Feb 1, 2024 (funding), locking users out mid-search; later acquired by BOLD and relaunched cheap (~$71/yr). Users reported duplicate sprays (15+ applications to one posting) ([LoopCV post-mortem](https://blog.loopcv.pro/what-happened-to-sonara/)).
- **Massive (usemassive.com)** ($59/mo) — Trustpilot 2.3/5: ~3% interview rate, applies weeks after posting, ignores seniority filters, applies via proxy email (@neuronmail.io) that gets spam-filtered, $10 refunds after promising 14-day guarantee ([Trustpilot](https://www.trustpilot.com/review/usemassive.com), [Sorce review](https://www.sorce.jobs/reviews/massive)).
- **JobRight.ai** ($29/mo Turbo) — matching quality above average per Reddit (r/jobsearchhacks, r/GetEmployed), but AI resume bullets hallucinate metrics, phantom/expired listings persist, auto-apply agent waitlist-gated, cancellation friction ([Remote Job Assistant review](https://www.remotejobassistant.com/blog/jobright-ai-review)).
- **Teal** — well-liked for tracker + per-JD tailoring/keyword scoring; free tier substantial, paid ~$9/wk generally judged unnecessary unless high-volume ([Teal reviews](https://resumejudge.com/blog/tealhq-review/)).
- **LoopCV** — oldest auto-apply (since 2019), 4.7 Google rating, more configurable, survives as the "least bad" auto-applier ([LoopCV](https://blog.loopcv.pro/loopcv-alternatives/)).
- **Final Round AI** ($25+/mo, live interview copilot) — most controversial: "stealth mode" reportedly visible during Zoom screen-share despite "undetectable" claims; 17% one-star on Trustpilot (billing, generic answers) ([Remote Job Assistant](https://www.remotejobassistant.com/blog/final-round-ai-review), [Trustpilot](https://www.trustpilot.com/review/finalroundai.com)).
- **hiring.cafe** — not AI, but the job *source* HN/Reddit actually loves: aggregates directly from company career pages (kills ghost/repost listings), granular filters, salary transparency ([HN thread](https://news.ycombinator.com/item?id=42803304)).

## 4. What works vs. what doesn't — the evidence

**The flood is real and priced in:**
- LinkedIn: applications up 45%+ YoY, ~9,500–11,000 applications/minute; single remote roles pull 1,200+ applicants; recruiters "drinking through a fire hose" ([CNBC](https://www.cnbc.com/2025/10/29/recruiters-are-drinking-through-a-fire-hose-of-job-applications-experts-say.html), [eWeek](https://www.eweek.com/news/ai-job-applications-linkedin/)).
- HN hiring managers: 800 applications in 24h for one startup role, ~30% ghost/fraudulent; 50% of cover letters obviously AI ("passionate about $VARIABLE1") → instant rejection ([HN](https://news.ycombinator.com/item?id=41756371)).

**Numbers:**
- Baseline response rate 2–5%; 75% of applications get zero response (95% in tech); ~3% of applications → interview (CareerPlug, 10M applications) ([scale.jobs benchmarks](https://scale.jobs/job-application-response-rate), [Zipply data](https://www.tryzipply.com/blog/auto-apply-tools-are-hurting-your-job-search)).
- Targeted applications get **3–5x** the response rate of auto-apply spray. Referrals: ~1 in 16 referred candidates hired vs 1 in 152 ATS cold applicants — **9.5x** ([refer.me data](https://www.refer.me/blog/do-job-referrals-actually-work-data-behind-response-rates)); "one referral ≈ 40 cold applications" ([Interview Guys](https://blog.theinterviewguys.com/state-of-job-search-2025-research-report/)).
- Contrast case study: hand-tailored AI-assisted (69 apps → 20 interviews) vs LazyApply (47 apps → 0 interviews) vs Massive (~3% interview rate).

**ATS reality (important myth-bust):**
- Greenhouse/Lever do essentially **no automatic keyword scoring** — humans read applications with scorecards; 92% of recruiters (SHRM 2024) confirm ATSs don't auto-reject on keywords or formatting ([Hiration](https://www.hiration.com/blog/ats-auto-reject-resume-myth/), [FastApply Greenhouse guide](https://blog.fastapply.co/how-to-beat-greenhouse-ats-2026)). The machine rejects you in exactly one place: **knockout questions** (visa, location, hard requirements).
- Keywords still matter differently: recruiters *search* the ATS database — a missing keyword makes you unsearchable, not deleted. So tailoring = honest keyword coverage + parseable format, not keyword stuffing.
- But: ~88% of companies use some AI in initial screening and ~40% of applications are filtered before human review via knockouts/rankers — and ATS vendors (Greenhouse, Lever, Workday) now run **bot detection and velocity filters** flagging fast/uniform/same-IP submissions ([Zipply](https://www.tryzipply.com/blog/auto-apply-tools-are-hurting-your-job-search)).

**Employer counter-offensive (2025–2026):**
- 74% of hiring managers have detected AI content; 62% reject unpersonalized AI resumes; ~20–25% reject on principle for AI cover letters ([US Chamber](https://www.uschamber.com/co/run/human-resources/hiring-ai-job-applications), [Resume Now](https://www.resume-now.com/job-resources/careers/ai-applicant-report)).
- 61% of companies run AI-detection during interviews; 39% shifted to more in-person interviews; Greenhouse launched "Real Talent" identity-verification/fraud detection ([Greenhouse 2026 AI Hiring Report](https://www.greenhouse.com/newsroom/an-ai-trust-crisis-70-of-hiring-managers-trust-ai-to-make-faster-and-better-hiring-decisions-only-8-of-job-seekers-call-it-fair), [HR Dive](https://www.hrdive.com/news/the-ai-race-has-fostered-better-hiring-decisions-and-mistrust/805994/)).
- Prompt-injection resume tricks → cross-company blacklists (Manpower et al.).

## 5. The consensus playbook (high-signal sources)

Converging recommendation across recruiter data, the Interview Guys report, HN practitioners, and post-mortems of failed auto-apply runs:

1. **Volume**: 10–20 *targeted* quality applications/week (roles you're ~80%+ qualified for), not 100s. Median search: ~68 days, ~32 apps → 4 interviews for the median successful seeker.
2. **Time split**: ~80% networking/referrals/direct outreach, ~20% applying. Referral acceptance rates: alumni 82%, colleagues 89%, cold outreach 23%.
3. **Source jobs fresh and direct**: company career pages / hiring.cafe / scraped-and-LLM-ranked feeds within 24–72h of posting; Easy Apply is the lowest-signal channel (HN hiring managers check it last).
4. **AI adds leverage in**: discovery/ranking (scrape + LLM scoring), keyword-gap analysis and resume tailoring (human-verified, no invented facts), first drafts of cover letters/outreach (then personalize), mock interviews (voice mode), tracking/CRM, company research briefs.
5. **AI actively hurts in**: unedited generative output (template artifacts = instant reject), mass auto-apply (velocity flags, duplicate applications, reputation damage, LinkedIn bans), hallucinated resume claims (fraud databases), live interview copilots (detectable, blacklisting), prompt injection (blacklisting).

## Key takeaways for building a personal job-search agent

1. **Automate discovery, not submission.** The winning architecture (scrape → LLM-rank → human applies to top matches) is proven; auto-submit is where every documented failure lives. LazyApply 47→0; hand-tailored 69→20 interviews.
2. **Use JobSpy** ([speedyapply/JobSpy](https://github.com/speedyapply/JobSpy)) as the scraping layer — Indeed endpoint most reliable; use proxies for LinkedIn; hiring.cafe-style direct career-page sources beat aggregators on freshness and ghost-job rate.
3. **LLM-score each posting against a structured profile** (1–10 + reason + extracted requirements), dedupe by URL, deliver a daily ranked digest. GitHub Actions + Claude + Notion/SQLite is a zero-hosting reference design.
4. **Tailor per posting via keyword-gap analysis, never fabrication.** Have the agent diff JD terms against the master resume, propose reworded (true) bullets, and require human approval. Hallucinated metrics are the #1 reported AI failure and now trigger cross-company blacklists.
5. **Optimize for recruiter search + knockout questions, not a mythical keyword auto-rejector.** Greenhouse/Lever are human-read; the only hard machine gate is knockout questions. Missing keywords = unsearchable, not rejected.
6. **Freshness beats volume**: apply within 24–72h of posting; Massive's biggest complaint was applying weeks late. Build recency into ranking.
7. **Throttle everything**: 5–10 quality applications/day max; never automate logged-in LinkedIn actions (velocity detection, extension fingerprinting, permanent bans; enforcement hardened late 2025).
8. **Add a referral/outreach module** — the highest-ROI automation nobody builds: for each top-ranked job, find alumni/2nd-degree contacts and draft (human-edited) outreach. Referrals convert 9.5x better than cold ATS applications.
9. **Cover letters: AI draft + mandatory human pass.** 63% of recruiters accept personalized AI-assisted letters; 80% reject generic ones; template artifacts are instant rejection.
10. **Include an interview-prep agent (fully legitimate) and a tracker.** Voice-mode mock interviews with JD + resume context replicate what paid tools charge $25+/mo for; log every application (company, date, version sent, follow-up date) — the median successful search is ~68 days and ~32 applications, so persistence infrastructure matters as much as generation.
