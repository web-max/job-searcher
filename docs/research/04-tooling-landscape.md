# Tooling Landscape: Personal Job-Search Automation System

*Research compiled 2026-07-16. Prices/versions verified against 2025–2026 sources. Bias of this report: cheap, low-ban-risk, human-in-the-loop for a single job seeker.*

## 1. Browser automation for LinkedIn — detection, bans, and whether you need anti-detect tooling

**Verdict up front: an individual job seeker should NOT automate LinkedIn actions. Use a normal logged-in browser profile and send connections/messages manually.** The ban asymmetry is brutal and the payoff is small at solo volume.

**What LinkedIn detects (2025–2026 enforcement is much harder than legacy guides suggest):**
- ML behavioral biometrics: analyzes action *rhythm* — timing regularity, mouse/scroll patterns, the "mathematical precision that defines a script." Detection rates reportedly rose ~340% 2023→2025.
- Device/location/IP consistency, headless-browser artifacts (`navigator.webdriver`, CDP listeners), and prohibited third-party extensions (LinkedIn's User Agreement explicitly bans scraping, headless browsers, and automation).
- Volume anomalies: 200+ connection requests/day or 100 messages within hours is flagged "immediately."

**Ban reports / restriction rates:**
- One tester's data: **~23% restriction rate within 90 days** across 50 automated accounts. Tier-3 permanent bans have <15% appeal-recovery success.
- The unofficial Voyager API (see §4) reportedly gets accounts **banned within 3–7 days**.
- LinkedIn **banned Apollo.io and Seamless.ai** integrations in 2025; **sued Proxycurl (Nubela) Jan 2025**, which shut down by July 2025 (details §4).

**Safe rate limits people stay under (for manual/semi-manual activity):**
- **~100 connection requests/week** is the hard cap (resets weekly). Stay well under.
- Warm accounts gradually; randomize timing; never batch.

**Headless vs headful:** Headless is more detectable (fingerprint + automation artifacts). If you automate anything, headful with a real persistent user-data-dir profile is safer — but for LinkedIn specifically the safest posture is *human-in-the-loop*: the tool drafts messages / opens the right page, **you** click send. Semi-automation keeps the human's genuine behavioral fingerprint and keeps you inside ToS-grey rather than ToS-violating territory.

**Stealth / anti-detect tooling landscape (what each is, honest assessment):**

| Tool | Type | Notes |
|---|---|---|
| **Playwright-stealth / puppeteer-stealth** | Patch libraries | Increasingly detected; the arms race moved past them. |
| **Patchright** | Patched Chromium (drop-in Playwright) | Strips `navigator.webdriver`/CDP artifacts at binary level. Current best OSS Chromium option. |
| **undetected-chromedriver** | Patched ChromeDriver (Selenium, Python-only) | Patches driver binary + Chrome flags. Still widely used; aging. |
| **Camoufox** | Anti-detect Firefox (OSS) | Was strong; **~1-year maintenance gap as of 2026**, degraded due to stale Firefox base + new fingerprint inconsistencies. |
| **nodriver** | Successor to undetected-chromedriver | Newer evasion generation. |
| **Multilogin / GoLogin / AdsPower / Octo / Kameleo** | Commercial anti-detect browsers | Built for managing *many* profiles (multi-accounting). Subscription cost, aimed at agencies/growth-hackers. |

**Do you need any of them? No.** Anti-detect browsers exist to run *many fake profiles at scale* — that is the exact behavior LinkedIn sued over and the opposite of what a job seeker wants. For one person on one real account, an anti-detect browser increases risk (it looks like multi-accounting) while solving a problem you don't have. **Correct call: your own real Chrome profile, logged in, manual sending.** Reserve any automation for *reading/prep* (drafting, ranking) not *acting*.

Sources: [Cleverly](https://www.cleverly.co/blog/why-linkedin-automation-tools-get-your-account-banned-and-what-to-do-instead), [PhantomBuster](https://phantombuster.com/blog/social-selling/linkedin-automation-tool-warning/), [GetSales safety guide](https://getsales.io/blog/linkedin-automation-safety-guide-2026/), [LinkedIn prohibited software](https://www.linkedin.com/help/linkedin/answer/a1341387), [Camoufox](https://github.com/daijro/camoufox), [Scraping Central stealth comparison](https://scrapingcentral.com/blogs/stealth-browser-comparison), [Castle.io evolution](https://blog.castle.io/from-puppeteer-stealth-to-nodriver-how-anti-detect-frameworks-evolved-to-evade-bot-detection/).

---

## 2. AI browser-agent frameworks (form-filling job applications)

| Tool | Lang | Model | Maturity | Cost | Best for |
|---|---|---|---|---|---|
| **browser-use** | Python | OSS lib, BYO LLM | Most popular OSS; **89.1% WebVoyager** (SOTA) | Free lib + your LLM tokens | Goal-driven NL agent loops; general automation |
| **Stagehand** | TS | OSS SDK, by Browserbase | Mature; **caches action→selector mappings** to avoid re-calling LLM per page (big cost saver) | Free SDK; pushes you to Browserbase cloud | Repeatable structured flows |
| **Skyvern** | Python | Vision-model, DOM-agnostic | **85.85% WebVoyager (v2.0); best at form-filling specifically** — screenshots + vision so it "sees" forms like a human | OSS + paid cloud | **Job-application form filling** (its sweet spot) |
| **Playwright MCP** (microsoft/playwright-mcp) | any MCP host | your LLM (Claude Code, etc.) | Released Mar 2025; 32k★, 2M weekly npm; 23 tools; Apache-2.0 | **$0** tool cost; but ~114K tokens/task (heavy) vs 27K CLI | Driving a browser from Claude Code as orchestrator |
| **Anthropic Computer Use** | API | Claude | GA tool | Standard tool-use token pricing | Vision GUI control when DOM fails |
| **OpenAI Operator** | — | — | **Deprecated Aug 2025**; folded into ChatGPT "agent mode" | — | (No longer a standalone API) |

**Hosted browser infra:**
- **Browserbase** — managed Chromium fleet, stealth mode, CAPTCHA solving, proxy rotation, session replay. $40M Series B (Jun 2025). Recommended backend for Stagehand. Paid.
- **Steel.dev** — OSS headless browser API for agents; sub-second startup, sessions up to 24h, **free tier 100 browser-hours/month**, self-hostable.

**Suitability for job apps:** Skyvern (vision, form-native) is the strongest fit for actually filling application forms. But note: LinkedIn Easy Apply and many ATS forms are exactly where bot-detection lives, and a botched auto-application is worse than none. For a solo seeker, use these agents on **non-LinkedIn ATS forms** at most, and keep a human approving each submit. Playwright MCP + Claude Code is the cheapest "orchestrator drives a real browser you watch" path.

Sources: [Framework Wars (DEV)](https://dev.to/stevengonsalvez/browser-tools-for-ai-agents-part-2-the-framework-wars-browser-use-stagehand-skyvern-4gn), [Skyvern](https://github.com/skyvern-ai/skyvern), [Stagehand](https://github.com/browserbase/stagehand), [Playwright MCP](https://github.com/microsoft/playwright-mcp) + [morphllm cost note](https://www.morphllm.com/playwright-mcp), [Steel](https://steel.dev/), [Browserbase](https://www.browserbase.com/stagehand), [firecrawl best browser agents](https://www.firecrawl.dev/blog/best-browser-agents).

---

## 3. Job data acquisition WITHOUT fragile scraping

**This is where the system should live — clean APIs, no ban risk.** Priority order: ATS public JSON APIs → remote-job APIs → aggregators → (JobSpy as fallback).

### 3a. JobSpy (`python-jobspy`)
- Scrapes LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter, Bayt, BDJobs concurrently. `pip install python-jobspy`.
- Params: `site_name`, `search_term`, `location`, `distance` (mi, default 50), `job_type` (fulltime/parttime/internship/contract), `is_remote`, `results_wanted`, `easy_apply`, `description_format` (markdown/html), `proxies`.
- **Limits:** ~1000 jobs/search cap per board. **Indeed = best/no rate limiting.** **LinkedIn rate-limits ~page 10 on a single IP; proxies basically mandatory.** HTTP 429 = blocked. Treat LinkedIn via JobSpy as unreliable and ToS-grey.
- Source: [PyPI](https://pypi.org/project/python-jobspy/), [GitHub speedyapply/JobSpy](https://github.com/speedyapply/JobSpy).

### 3b. ATS public JSON APIs (the durable, no-auth backbone — use these first)
No OAuth, no partner approval; GET returns published jobs. Every major ATS exposes one:

- **Greenhouse:** `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true` (single job: `/jobs/{id}`). Careers page pattern `boards.greenhouse.io/{board_token}`.
- **Lever:** `https://api.lever.co/v0/postings/{company}?mode=json` — filters: `team`, `department`, `location`, `commitment`, `level`, `skip`, `limit`.
- **Ashby:** `https://api.ashbyhq.com/posting-api/job-board/{company}?includeCompensation=true` (best salary data).
- **Workable:** public careers endpoints (account + jobs, plus companion locations/departments endpoints).
- **Helper libs:** [plibither8/jobber](https://github.com/plibither8/jobber) wraps Ashby/Greenhouse/Lever/etc.
- Sources: [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html), [Cavuno ATS list](https://cavuno.com/blog/ats-platforms-public-job-posting-apis), [fantastic.jobs](https://fantastic.jobs/article/ats-with-api).
- **Catch:** you must know *which companies* use *which ATS*. Build a target-company→ATS map, then poll each board. This is the highest-signal, lowest-risk source.

### 3c. Remote-job APIs (free, JSON)
- **Remotive:** `https://remotive.com/api/remote-jobs` (optional `?category=`, `?search=`, `?limit=`). All active listings, sorted by date.
- **RemoteOK:** `https://remoteok.com/api` (JSON; first element is legal/metadata — skip it; attribution required).
- **Himalayas:** public JSON jobs feed (aggregated alongside Arbeitnow, Jobicy in the wild).
- **Arbeitnow / Jobicy:** additional free public feeds.
- Sources: [Remotive](https://remotive.com/), [RemoteOK Intelligence API note](https://apify.com/benthepythondev/remote-jobs-intelligence/api).

### 3d. Aggregator APIs (free tiers)
- **Adzuna:** `https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id=...&app_key=...&what=...&where=...` — **free ~1,000 calls/month**, 16 countries (strongest UK/W-Europe). [developer.adzuna.com](https://developer.adzuna.com/).
- **JSearch (RapidAPI / OpenWeb Ninja):** real-time Google-for-Jobs aggregation + salary data. Free tier, **no credit card**. [JSearch](https://www.openwebninja.com/api/jsearch), [RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch).
- **Google Jobs via SerpApi:** `https://serpapi.com/search?engine=google_jobs&q=...&location=...&api_key=...`. Free tier ~100 searches/month. [SerpApi Google Jobs](https://serpapi.com/google-jobs-api).

### 3e. HN "Who's Hiring" parsing
- **Algolia HN Search API** (no auth, 10,000 req/hr): `http://hn.algolia.com/api/v1/search_by_date?tags=comment,story_{THREAD_ID}&hitsPerPage=1000` — pull all comments of the monthly "Ask HN: Who is hiring?" thread, then parse each comment as one posting.
- Find the thread id via `https://hn.algolia.com/api/v1/search?query=Ask HN Who is hiring&tags=story` (posted by user `whoishiring`, 1st of each month).
- **RSS shortcut:** `https://hnrss.org/whoishiring/jobs` (jobs), `/hired`, `/freelance`.
- Sources: [hn.algolia.com/api](https://hn.algolia.com/api), [hnrss](https://hnrss.github.io/).

---

## 4. LinkedIn data specifically — what's actually feasible

- **Official LinkedIn API:** effectively closed. Job/profile data requires partner programs you won't get as an individual. Treat as unavailable.
- **`linkedin-api` (Tom Quirk, unofficial Voyager API):** `pip install linkedin-api`. Logs in with your creds and hits LinkedIn's internal Voyager endpoints. **High ban risk — accounts reportedly banned within 3–7 days.** Violates ToS. Do not point it at your real account. [PyPI](https://pypi.org/project/linkedin-api/), [ban writeup](https://medium.com/@mhmdjmala51/how-to-get-banned-with-linkedin-api-python-c9ecaec93f5e).
- **Proxycurl — DEAD.** LinkedIn sued Nubela **Jan 24, 2025** (N.D. Cal.; CFAA, breach, fraud, Lanham, UCL — alleging hundreds of thousands of fake scraping accounts). Settled mid-2025; **service shut down July 2025**, data deleted. Founder: "no winning in fighting this." [Goodbye post](https://nubela.co/blog/goodbye-proxycurl/), [Startuphub](https://www.startuphub.ai/ai-news/startup-news/2025/the-1-linkedin-scraping-startup-proxycurl-shuts-down).
- **Successor people-data APIs (for reference, not recommended at solo scale):** ScrapIn, Apify actors, Bright Data (real-time "URL in → JSON out"); Coresignal, People Data Labs (bulk); Linked API, Unipile (account-based, paid, still ToS-grey).
- **Recommended for a job seeker:** **manual export + browser-assisted lookup.** Download your own LinkedIn data export; look up recruiters by hand in your logged-in session. Don't build LinkedIn data ingestion into an automated pipeline — the legal/ban risk dwarfs the value.

Sources above + [Clura LinkedIn API overview](https://clura.ai/blog/linkedin-api), [linkedapi Proxycurl alternatives](https://linkedapi.io/guides/proxycurl-alternatives).

---

## 5. LLM APIs for the pilot — DeepSeek vs Claude, with cost math

### DeepSeek API (verified from docs 2026-07-16)
- **Base URL (OpenAI-compatible):** `https://api.deepseek.com` (also Anthropic format at `/anthropic`).
- **Current models:** `deepseek-v4-flash` (cheap) and `deepseek-v4-pro`. **Legacy `deepseek-chat` / `deepseek-reasoner` deprecate 2026-07-24** (they map to v4-flash non-thinking/thinking). Both v4 models: 1M context, tool calls + JSON mode.
- **Pricing per 1M tokens:** `deepseek-v4-flash`: **$0.14 input / $0.28 output** (cache-hit input ~$0.0028); `deepseek-v4-pro`: $0.435 / $0.87.
- Source: [DeepSeek pricing docs](https://api-docs.deepseek.com/quick_start/pricing).

### Claude
- Haiku 4.5 $1.00/$5.00 per 1M in/out; Sonnet 4.6 $3/$15; Opus 4.8 $5/$25. Or **Claude Code as orchestrator** (no separate key needed).

### Cost estimate for the target workload (200 job matches ranked + 50 drafts/week)
Assumptions: ranking a job ≈ 1.5K input + 0.3K output; a tailored draft ≈ 3K input + 0.7K output → weekly ~450K input + ~95K output tokens.

| Model | Weekly cost | Monthly (~4.3×) |
|---|---|---|
| **DeepSeek v4-flash** | ≈ **$0.09/wk** | **~$0.39/mo** |
| **Claude Haiku 4.5** | ≈ **$0.93/wk** | **~$4/mo** |
| **Claude Sonnet 4.6** | ≈ **$2.78/wk** | **~$12/mo** |

**Takeaway:** cost is negligible either way. Use **DeepSeek v4-flash for bulk ranking** and a stronger model (Claude, or v4-pro) **for the 50 drafts** where writing quality matters. Prompt-cache the stable rubric/profile prefix.

---

## 6. Orchestration options

| Option | Fit | Notes |
|---|---|---|
| **cron + Python scripts** | Simplest, most controllable, $0 | Poll ATS/aggregator APIs nightly, rank with DeepSeek, write to tracker, draft messages. Best for a developer. |
| **n8n** | Popular, many ready templates | Self-host free. Templates: [#9602](https://n8n.io/workflows/9602-automate-job-search-with-linkedin-google-sheets-and-ai/), [#3543](https://n8n.io/workflows/3543-automated-linkedin-job-hunter-get-your-best-daily-job-matches-by-email/), [#3724](https://n8n.io/workflows/3724-smart-job-search-resume-scoring-and-tailoring-with-openai-apify-and-airtable/), [#11215](https://n8n.io/workflows/11215-automate-job-applications-with-ai-resume-tailoring-using-gpt-4o-linkedin-and-gmail/), [#9793](https://n8n.io/workflows/9793-automating-job-searches-on-linkedin-and-x-then-saving-results-to-notion/). Most rely on Apify LinkedIn scrapers (paid, ToS-grey) — swap those nodes for the ATS/aggregator APIs in §3. |
| **Claude Code as orchestrator + skills** | Strong | Skills for "rank jobs", "draft outreach"; MCP for Gmail/Notion; drives Playwright MCP for the rare browser task. Human-in-the-loop by design. |
| **Trackers** | Notion / Airtable / Google Sheets / SQLite | Sheets = zero-friction + free API; Airtable = better views; SQLite = local + private. |
| **Gmail drafts** | Gmail API `users.drafts.create` | Create drafts, never auto-send — the human-in-the-loop seam for email outreach. |

---

## 7. Email finding / verification for recruiter outreach

| Tool | Free tier | Notes |
|---|---|---|
| **Hunter.io** | 50 unified credits/mo (1 credit = find, 0.5 = verify) | Clean API: domain search, email finder, verifier. [hunter.io](https://hunter.io/). |
| **Apollo.io** | Generous free email credits under fair-use | Bigger contact DB + sequencing. [comparison](https://leadmagic.io/comparisons/hunter-vs-apollo). |
| **Permutation + verify (DIY, ~free)** | Generate `first.last@`, `flast@`, `first@` patterns → verify via SMTP/MX or a verifier API | Cheapest path at solo volume. |

**Recommendation:** Apollo free tier for finding + Hunter credits for verifying, or permutation→verify DIY.

---

## Recommended reference architecture (solo job seeker: cheap, low-ban-risk, human-in-the-loop)

1. **All ingestion is API-based.** Never scrape LinkedIn in an automated loop. ATS JSON APIs + remote-job APIs cover most quality roles with zero ban risk.
2. **No anti-detect browser, no Proxycurl-style people API, no unofficial `linkedin-api`.** All either dead, sue-bait, or 3–7-day-ban material.
3. **LLM does reading and drafting, not acting.** Rank/draft with LLMs; humans send.
4. **Every outbound action passes a human gate** (Gmail drafts, manual LinkedIn send).
5. **Cost stays ~$1–12/month.**

**Stack shortlist:** Python + cron (or Claude Code) · ATS/remote/aggregator JSON APIs · DeepSeek v4-flash (rank) + stronger model (draft) · SQLite/Sheets tracker · Gmail drafts · Apollo/Hunter free tiers · your own logged-in Chrome for the LinkedIn touch. Skip: anti-detect browsers, Proxycurl-class APIs, `linkedin-api`, any auto-send.
