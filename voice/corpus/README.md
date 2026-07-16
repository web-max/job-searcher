# Voice corpus

Drop samples of **her own writing** in this folder, then run `python -m agent voice-build`.

Accepted formats:
- `.txt` / `.md` files — one message per file, or several messages separated by a line of `---`
- `.eml` files — individual emails
- `.mbox` — a Google Takeout export of her **Sent Mail** (Gmail → Google Takeout → Mail → select "Sent")

What to include (20+ messages is enough, 50+ is great):
- Sent emails to acquaintances and colleagues (the professional-but-real register)
- Longer texts/DMs she's written
- Anything she wrote for work: Slack messages, notes, updates

What NOT to include:
- Other people's writing (quoted replies are stripped automatically, but don't rely on it)
- Anything she isn't comfortable having summarized into a style profile

**Consent matters.** This must be her data, exported by her or with her explicit OK.
The corpus stays local — nothing here is uploaded except small excerpts inside LLM
prompts when drafting her messages.

The build produces:
- `voice/voice_profile.md` — measured habits (greeting/sign-off, sentence rhythm,
  punctuation, pet phrases) + real samples, injected into every drafting prompt
- `voice/whitelist.json` — words from the AI-tell lists that she genuinely uses,
  so the linter doesn't sand off her actual voice
