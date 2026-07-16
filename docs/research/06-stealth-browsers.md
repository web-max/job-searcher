# Stealth Browsers for Assisted Apply: Research (2026-07-16)

Multi-agent research run (3 independent web sweeps + synthesis, star counts
verified against the GitHub API on 2026-07-16). Question: should the assisted
apply form-filler use a stealth browser instead of plain Playwright, and which?

## Decision

**Patchright** (`pip install patchright && patchright install chromium`), with
real installed Chrome preferred over bundled Chromium (`channel="chrome"`).
Implemented in `agent/apply.py`: Patchright is tried first, plain Playwright is
the fallback. One-line import swap; the whole Playwright API is unchanged.

## Do we even need stealth here?

Barely — and that's worth being honest about. This threat model is the mildest
possible: a headed visible browser, a residential home IP, a real human driving
mouse/keyboard and pressing submit, low volume, no LinkedIn. Every strong bot
signal (datacenter IP, headless flags, superhuman timing, volume) is absent by
construction. The one residual false-positive vector is **passive automation
fingerprinting** — CDP leaks like `Runtime.enable` and `navigator.webdriver`
that fire regardless of how human the behavior is, and can trip Cloudflare/ATS
walls before a human ever gets to prove otherwise. That is exactly and only
what Patchright patches, at zero behavior change and zero cost. Cheap insurance;
no proxies or CAPTCHA solvers needed — a human clears any challenge that appears.

## The products from memory

- **Paid ~$20/mo AI-agent stealth browser** = **Browserbase** Developer tier
  ($20/mo: 100 browser-hrs, basic stealth, auto-CAPTCHA; browserbase.com/pricing).
  Its famous open-source sibling is **Stagehand** (`browserbase/stagehand`,
  ~23.5k stars). NOT used here: Browserbase & friends (Steel cloud, Hyperbrowser,
  Anchor, Kernel) are cloud browsers on datacenter IPs — moving off the trusted
  residential IP would *increase* false positives for this use case.
- **Open-source one with ~7–15k stars** = most likely **Camoufox**
  (`daijro/camoufox`, ~10.1k stars), a Firefox-based anti-detect browser.
  Runner-up match: `steel-dev/steel-browser` (~7.3k), the self-hostable twin of
  the paid Steel cloud.

## Candidates compared (stars verified 2026-07-16)

| Tool | Stars | Verdict for this repo |
|---|---|---|
| **Patchright** (`Kaliiiiiiiiii-Vinyzu/patchright`, `-python`) | 3.8k / 1.4k | **Chosen.** Drop-in `patchright.sync_api`, Chromium, actively maintained, patches CDP/`Runtime.enable`/isolated-context leaks. Benchmarks ~25/31 vs vanilla Playwright ~24/31 on detection suites, with the passive-fingerprint holes closed. |
| Camoufox (`daijro/camoufox`) | 10.1k | Stronger fingerprint evasion (esp. DataDome) but Firefox + adapter API → re-test every ATS form for Firefox quirks. **Escalation fallback** if Patchright ever proves insufficient. |
| nodriver / Zendriver | 4.5k / 1.4k | Highest raw evasion but async-only, non-Playwright API → full rewrite. Overkill. |
| SeleniumBase UC / undetected-chromedriver | 12.9k / 12.8k | Selenium world; UC stale (last push 2025-07). Rewrite required. |
| rebrowser-patches | 1.4k | Same idea as Patchright, barely beats vanilla, Node-first. Superseded. |
| Lightpanda / browser-use / puppeteer-extra-stealth / steel-browser | — | Wrong category (headless infra / LLM agent / Node+stale / cloud). |

## Patchright integration notes (the gotchas)

- Prefer `channel="chrome"` (real Chrome) over bundled Chromium — measurably
  better stealth. Keep `headless=False`.
- Do NOT add hand-rolled stealth flags (`--disable-blink-features=AutomationControlled`)
  or stealth JS init scripts on top — Patchright already handles it and extra
  tampering adds detectable signals.
- **The one API difference:** `page/frame.evaluate` runs in an *isolated* JS
  world by default and the Console API is disabled. DOM access (querySelector,
  setAttribute, getComputedStyle) works fine — which is all our `_COLLECT_JS`
  uses — but code reading main-world page globals (`window.someAppVar`) or
  relying on `console.log` silently breaks; opt out per-call with
  `evaluate(..., isolated_context=False)` only where truly needed.
- `locator.fill` / `set_input_files` unchanged. Closed shadow roots supported.
  Chromium/Chrome only — no Firefox/WebKit.
- Optional future upgrade: `launch_persistent_context` so the browser looks
  like a returning user (cookies/history).
