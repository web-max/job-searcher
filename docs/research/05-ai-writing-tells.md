# AI Writing Tells & Humanization Playbook for Short Professional Messages

Research report. Scope: LinkedIn messages, cold emails, cover letters. Sources 2023–2026, weighted to 2025–2026.

## 1. The Canonical Catalog of AI Tells

### 1.1 Vocabulary tells
The best-curated source is [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (editor-maintained by WikiProject AI Cleanup from thousands of confirmed AI submissions). High-density "AI vocabulary": **delve, tapestry, testament, landscape, realm, robust, pivotal, crucial, intricate, meticulous(ly), fostering, bolstered, boasts, garner, underscore, showcase, vibrant, enduring, interplay, align with, enhance, highlight, emphasizing, valuable insights**.

Corpus linguistics backs this: 21 "focal words" spiked in post-ChatGPT scientific English ([Orlowitz roundup](https://medium.com/@jakeorlowitz/delving-into-the-load-bearing-tapestry-of-ais-overused-words-a2a0024cee9a)). "Delve" jumped ~654% 2020→2023 but **dropped off sharply in 2025** as models were tuned away ([Walter Writes](https://walterwrites.ai/most-common-chatgpt-words-to-avoid/)) — word lists decay; structural tells persist.

[Pangram Labs](https://www.pangram.com/blog/walking-through-ai-phrases) measured phrase over-representation vs human baseline: "vibrant tapestry" (17,000x), "In the ever-evolving" (11,000x), "serves as a powerful" (10,000x), "serves as a testament" (4,000x), "important to note" (3,000x).

**Outreach/application-specific phrase tells** ([AiSDR](https://aisdr.com/blog/words-to-avoid-so-you-dont-sound-like-ai/), [topo.io](https://www.topo.io/blog/ai-email-generation-a-complete-guide-on-how-to-not-sound-like-an-ai), [scale.jobs](https://scale.jobs/blog/write-cover-letter-using-ai-without-sounding-like-bot)):
- "I hope this email/message finds you well" — "the official opening line of robots"
- "I am writing to express my strong interest in the [X] role at your esteemed organization"
- "I bring a unique blend of skills, passion, and dedication"
- "I thrive in fast-paced environments and am a team player"
- "adept," "tech-savvy," "cutting-edge," "spearheaded," "results-driven," "proven ability"
- "your company's mission deeply resonates with me / aligns with my values"
- "explore synergies," "circle back," "touch base"
- Weak CTAs: "I'd love to tell you more," "Let me know if interested"
- Leaked artifacts: "Let me know if you need any modifications! 🚀", "[add numbers here]"

### 1.2 Punctuation & typography tells
- **Em dashes** — the most famous 2025 tell ([Washington Post](https://www.washingtonpost.com/technology/2025/04/09/ai-em-dash-writing-punctuation-chatgpt/)). LLM em dashes are often space-surrounded and used where humans use commas; multiple per sentence is the strong signal. Frequency, not presence, is the tell.
- **Curly/smart quotes** in plain-text contexts — indicates paste from LLM rich-text output.
- **Colon proliferation**; the **bold-term-colon list pattern** ("**Scalability:** the system…").
- Excessive semicolons in casual registers; excessive boldface; emoji as decoration (🚀 especially); markdown artifacts in plain-text email.

### 1.3 Structural / rhetorical tells
- **Contrastive negation** ("It's not just X, it's Y"; "This isn't about X, it's about Y") — the hardest-to-suppress and most damning pattern ([GC AI](https://gc.ai/blog/ai-writing-pattern-to-know-contrastive-negation), [Forbes](https://www.forbes.com/councils/forbescommunicationscouncil/2026/06/05/the-one-ai-writing-pattern-that-is-killing-your-credibility/)). Fix: state what the thing *is*; delete the defensive setup.
- **Negative parallelism** ("Not only… but also…").
- **Rule of three** — triads everywhere; a third item added even when unnecessary ([GPTZero](https://gptzero.me/news/the-rule-of-three/)).
- **Sycophantic openers** — "Great question!", flattery-first outreach openers.
- **Summary closers** — "In conclusion," restating the message's own point.
- **"-ing" participle tails for fake depth** — "…, highlighting the importance of X", "…, ensuring seamless collaboration".
- **Significance inflation / puffery** — "stands as a testament," "plays a vital role," "evolving landscape."
- **Vague attribution** — "experts argue," "studies show" with no specifics.
- **Copula avoidance** — "serves as," "functions as," "represents," "boasts" instead of plain "is/are".
- **Templated uniformity** — every paragraph the same length; formula "Greeting → vague compliment → value prop → benefits → generic CTA."
- **Exhaustive hedging** — "It's important to note," qualifier stacks.
- **Regression to the mean** — specific facts smoothed into generic statements. In a cover letter: "could have been sent by any of 500 applicants."

### 1.4 Rhythm / statistical tells
Detectors and humans both key on **low perplexity** (predictable word choice) and **low burstiness** (uniform sentence lengths). Human burstiness ~0.6–1.2 vs GPT ~0.2–0.4; text where every sentence runs 15–18 words scores low ([QuillBot](https://quillbot.com/blog/ai-writing-tools/burstiness-and-perplexity/)). Human signals AI lacks: fragments, self-interruption, asides, mild imperfections, idiosyncratic word choices. "Perfectly smooth" error-free prose is itself a tell.

## 2. What Recruiters Say (2025–2026)

- **TopResume survey, 600 US hiring managers, May 2025** ([source](https://topresume.com/career-advice/ai-in-hiring-survey)): **19.6% would reject** AI-generated materials; **33.5% spot an AI resume in under 20 seconds**; 25% say cover letters should be AI-free.
- 62% say AI resumes **without personalization** often lead to rejection; 78% look for personalized details as the signal of genuine interest ([ResuFit](https://resufit.com/blog/can-recruiters-tell-if-you-used-ai-to-write-your-resume/)).
- **HuffPost recruiter interviews** ([source](https://www.huffpost.com/entry/recruiters-job-application-chatgpt_l_6723b4e1e4b0871068fe81ad)): ~25% of applications look AI-generated with "similar sentence structures" and identical anecdotes; recruiters catch leftover "[add numbers here]" placeholders.
- **The consensus nuance**: recruiters don't reject *AI use*; they reject *no signal about the person*. The flag is "copy-pasted, robotic, formulaic template."
- LinkedIn's own data: personalized recruiter messages get ~40% higher acceptance.

**Implication: the failure mode isn't "detected as AI," it's "detected as generic." Specificity (details only this sender/recipient pair could produce) is both the anti-tell and the response-rate driver.**

## 3. Humanization Techniques That Work

### 3.1 Few-shot voice cloning from the sender's own writing
- Provide 3+ real samples and have the model first *analyze* then *imitate*: (1) voice-print analysis — tone, sentence length & rhythm, vocabulary & recurring phrases, formality; (2) "Style DNA" summary; (3) draft; (4) self-critique loop ([Cyber Corsairs prompt](https://cybercorsairs.com/the-ultimate-chatgpt-voice-cloning-prompt/)).
- Academic reality check: [Catch Me If You Can? (2025)](https://arxiv.org/html/2509.14543v1) — 400+ real authors — LLMs approximate personal style adequately in **structured formats like email** (good news for this use case) but fail at informal blog/forum voice.
- **Two-step "describe then apply" beats raw few-shot**: produce an explicit style description, then generate under it with samples attached.

### 3.2 Prompt pattern (concrete)
```
Persona: "You are [NAME]. Below are N emails [NAME] actually sent. Match their
voice exactly — greeting habits, sign-off, sentence rhythm, formality."
Constraints: "Short sentences mixed with long ones. Plain 'is/are' over 'serves as'.
Under 120 words. Never use: [banned list]. No em dashes. No 'not just X but Y'.
No rule-of-three lists. No generic compliments."
Context (the real payload): recipient's role, the specific post/news being
referenced, the sender's genuine reason for writing, one concrete shared detail.
Goal: one specific, low-friction CTA.
```
**Key finding: context beats style instructions** — the model can't fake specificity; the system must inject real facts or output will be generic no matter the voice prompt.

### 3.3 Editing passes (the highest-leverage step)
1. **Delete pass** — hedges, stock transitions, sycophantic openers, summary closers, banned vocabulary.
2. **Rhythm pass** — vary sentence length aggressively; allow a fragment; break parallel triads.
3. **Specificity pass** — add numbers, names, dates, an opinion, "one lived detail" only the sender could supply.
4. **Read-aloud test** — any stumble or cringe line gets rewritten.

## 4. Tools: Humanizers and Detectors

- **"Humanizer" tools (Undetectable.ai, StealthGPT, etc.) are the wrong tool.** Independent tests: output "grammatically fine but lacking personality"; StealthGPT's own checker scored its output 88% human while GPTZero flagged it 100% AI ([aixradar](https://aixradar.com/stealthgpt-review/)); of 16 tools tested by one reviewer only 2 passed even the narrow bypass metric. They optimize *detector evasion* by injecting statistical noise — which reads worse to a human recruiter.
- **Detectors are noisy and the wrong target.** False-positive rates 0.24%–18% depending on tool/methodology; **Stanford (2023): 7 detectors mislabeled >half of human TOEFL essays as AI** (61.3% avg FPR on non-native English) ([The Markup](https://themarkup.org/machine-learning/2023/08/14/ai-detection-tools-falsely-accuse-international-students-of-cheating)). Short texts (LinkedIn-message length) are where all detectors are weakest. Recruiters don't run GPTZero on a 90-word message — they pattern-match on genericness in ~20 seconds. The correct objective is "specific, in the sender's voice, worth replying to."
- **Open-source resources:** [MimickMyStyle_LLM](https://github.com/Amirthavarshini-Dhanavel/MimickMyStyle_LLM) (includes a reusable StyleEvaluator), [definitive-llm-writing-style-guide](https://github.com/viktorbezdek/definitive-llm-writing-style-guide).

## 5. Building a Voice Profile from a Writing Corpus

Grounded in stylometry ([overview](https://www.johnmenick.com/writing/stylometry.html), [Nature 2025 human-vs-AI stylometric comparison](https://www.nature.com/articles/s41599-025-05986-3)).

**Features to extract (from sent-mail corpus):**
1. **Rhythm**: mean sentence length, **sentence-length variance (burstiness)**, fragment frequency, paragraph lengths, one-line-email frequency.
2. **Lexical**: characteristic 1–3-grams (pet phrases); contraction rate; filler tolerance ("just," "actually," "tbh").
3. **Punctuation habits**: em-dash rate, comma density, semicolon presence (most people: zero), exclamation rate, ellipsis, parentheticals, emoji.
4. **Ritual features**: greeting distribution ("Hi X," / "Hey" / bare name), sign-off distribution ("Best," / "Thanks!" / none), P.S. usage.
5. **Register**: formality by recipient type, hedging rate, directness, humor density, typo/casualness tolerance.
6. **Structure**: bullets ever? Lead with ask or context? Length by message type.

**Applying it:** inject measured stats + matched few-shot examples into the system prompt; use the same metrics as a post-generation **lint target** (draft's sentence-length σ, em-dash count, banned-word count vs the sender's own baseline). Match few-shot examples to the *genre* (cold email to a stranger, not a note to a friend).

## Appendix A — Banned/Suspect Word & Phrase List
Machine-readable version lives in `agent/tells.py` (BAN / FLAG / WATCH severity levels). Severity applies to short professional outreach. **Whitelist any term that appears in the sender's own corpus at comparable frequency — the goal is matching the sender's baseline, not zero usage.** Word lists decay as models get tuned; structural rules age slower.

## Appendix B — Structural Linter Checklist
Implemented in `agent/humanize.py`:
- Sentence-length std dev ≥ 6 words (or ≥ sender's σ); reject uniform rhythm.
- Zero contrastive negation ("not just X, it's Y"), zero "not only…but also".
- Max 1 triad (A, B, and C) per message; no triple-adjective runs.
- No "-ing" analysis tails (", highlighting/ensuring/underscoring…").
- Copula check: prefer is/are/has over serves as/functions as/boasts.
- No hedging preambles; lead with the claim/ask.
- Em dashes ≤ 1 per message unless the sender's own rate is higher.
- Straight quotes only; no markdown artifacts; no emoji unless in corpus.
- Greeting/sign-off match the sender's measured habits.
- No pleasantry/flattery opener; first sentence contains a specific, verifiable detail.
- No summary closer; end on the CTA; CTA is concrete (named times, single question).
- ≥1 detail only this sender could write; ≥1 detail only this recipient fits (the "swap test": the message must fail if mail-merged to another recipient).
- No vague attribution; no leaked assistant artifacts ("[insert", placeholder braces).
- Banned-list scan with sender-corpus whitelist override.
- Read-aloud test as the final human gate.
- Do NOT gate on AI-detector scores — unreliable at this length and optimizing them degrades human readability.
