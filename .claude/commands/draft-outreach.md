Draft one outreach message. Arguments: $ARGUMENTS (expected: kind, person, company, and any context).

1. Read voice/voice_profile.md and the matching template in templates/outreach/.
2. If no specific detail about the recipient was provided, STOP and ask for one (their post, shared background, company news) - the first sentence must contain one, and it roughly doubles reply rates. Offer to help find one from public info the user pastes in.
3. Draft following agent/outreach.py's SYSTEM rules, in her voice.
4. Lint it: `python -m agent lint` (pipe the draft in). Fix all high-severity findings.
5. Save via `python -m agent outreach ...` or write the outbox file directly in the same format.
6. Remind: read it aloud once, edit anything that doesn't sound like you, send it yourself, then log it.
