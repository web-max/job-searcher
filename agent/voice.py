"""Build a voice profile from a corpus of the job seeker's OWN writing.

The corpus lives in voice/corpus/ - plain .txt files (one message per file, or
messages separated by lines of ---), or .eml files, or an .mbox export from
Google Takeout. It must be HER writing, exported and provided by her.

Outputs:
  voice/voice_profile.md  - measured stats + few-shot samples, injected into
                            every drafting prompt
  voice/whitelist.json    - words from the flag lists she genuinely uses, so
                            the linter doesn't strip her real voice
"""
import email
import email.policy
import json
import mailbox
import re
import statistics
from collections import Counter

from . import tells
from .paths import VOICE_CORPUS_DIR, VOICE_PROFILE_PATH, VOICE_DIR

SIG_CUTOFFS = re.compile(r"^(--\s*$|Sent from my|Get Outlook for)", re.M)
QUOTE_LINE = re.compile(r"^\s*(>|On .+ wrote:|From: )", re.M)


def _clean_body(text: str) -> str:
    """Strip quoted replies and signatures, keep the author's words."""
    m = QUOTE_LINE.search(text)
    if m:
        text = text[: m.start()]
    m = SIG_CUTOFFS.search(text)
    if m:
        text = text[: m.start()]
    return text.strip()


def _from_eml(path) -> str:
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=email.policy.default)
    body = msg.get_body(preferencelist=("plain",))
    return _clean_body(body.get_content()) if body else ""


def _from_mbox(path) -> list:
    out = []
    for msg in mailbox.mbox(str(path)):
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                out.append(_clean_body(payload.decode("utf-8", errors="ignore")))
        except (UnicodeDecodeError, AttributeError, LookupError):
            continue
    return out


def load_corpus() -> list:
    docs = []
    if not VOICE_CORPUS_DIR.is_dir():
        return docs
    for path in sorted(VOICE_CORPUS_DIR.iterdir()):
        if path.name.startswith(".") or path.name == "README.md":
            continue
        if path.suffix == ".txt" or path.suffix == ".md":
            raw = path.read_text(errors="ignore")
            docs.extend(_clean_body(chunk) for chunk in re.split(r"\n-{3,}\n", raw))
        elif path.suffix == ".eml":
            docs.append(_from_eml(path))
        elif path.suffix == ".mbox":
            docs.extend(_from_mbox(path))
    return [d for d in docs if d and len(d.split()) >= 5]


def _sentences(text):
    return [s for s in re.split(r"(?<=[.!?\n])\s+", text) if s.strip()]


GREETING_RE = re.compile(r"^(hi|hey|hello|dear|good morning|good afternoon|yo)\b[^\n,!]*[,!]?", re.I)

# words too common in general English to count as a personal verbal tic
_COMMON_WORDS = {
    "about", "after", "again", "along", "always", "around", "because", "before",
    "being", "could", "doing", "email", "every", "first", "getting", "going",
    "gonna", "great", "happy", "having", "hello", "little", "maybe", "might",
    "morning", "never", "other", "people", "place", "please", "pretty", "really",
    "right", "should", "since", "something", "sorry", "still", "thanks", "there",
    "these", "thing", "things", "think", "though", "thought", "through", "today",
    "tomorrow", "totally", "trying", "wanted", "weekend", "where", "which",
    "while", "would", "yesterday",
}
SIGNOFF_RE = re.compile(
    r"\b(best|thanks so much|thanks|thank you|cheers|talk soon|warmly|sincerely"
    r"|xo+|x{1,3}|take care|love you)[,!.]?\s*$", re.I)


def analyze(docs: list) -> dict:
    all_sent_lengths, greetings, signoffs = [], Counter(), Counter()
    em_dash = exclaim = emoji_count = contractions = total_words = 0
    phrase_counter = Counter()

    for d in docs:
        sents = _sentences(d)
        all_sent_lengths.extend(len(s.split()) for s in sents)
        first_line = d.strip().splitlines()[0] if d.strip() else ""
        m = GREETING_RE.match(first_line.strip())
        if m:
            greetings[m.group(1).lower()] += 1
        # sign-off usually sits on one of the last three lines (above the name)
        for line in d.strip().splitlines()[-3:]:
            m = SIGNOFF_RE.search(line.strip())
            if m:
                signoffs[m.group(1).lower()] += 1
                break
        em_dash += d.count("—")
        exclaim += d.count("!")
        emoji_count += len(re.findall(r"[\U0001F300-\U0001FAFF]", d))
        words = d.lower().split()
        total_words += len(words)
        contractions += len(re.findall(r"\b\w+'(s|t|re|ve|ll|d|m)\b", d.lower()))
        # 1-3 word phrases she repeats - mined from the message BODY only,
        # so greeting/sign-off/name boilerplate doesn't drown real pet phrases
        lines = d.strip().splitlines()
        body_lines = lines[:]
        if body_lines and GREETING_RE.match(body_lines[0].strip()):
            body_lines = body_lines[1:]
        while body_lines and (SIGNOFF_RE.search(body_lines[-1].strip())
                              or len(body_lines[-1].split()) <= 2):
            body_lines = body_lines[:-1]
        tokens = re.findall(r"[a-z']+", "\n".join(body_lines).lower())
        for n in (1, 2, 3):
            for i in range(len(tokens) - n + 1):
                gram = " ".join(tokens[i:i + n])
                if n == 1 and (len(gram) < 5 or gram in _COMMON_WORDS):
                    continue
                phrase_counter[gram] += 1

    pet_phrases = [p for p, c in phrase_counter.most_common(200)
                   if c >= max(3, len(docs) // 4) and not all(w in
                   {"the", "a", "to", "of", "and", "in", "i", "you", "it", "is", "that", "for"}
                   for w in p.split())][:12]

    # which flag-list words and phrases does she actually use?
    corpus_text = " ".join(docs).lower()
    whitelist = [w for w in tells.FLAG_WORDS + tells.WATCH_WORDS
                 if re.search(rf"\b{re.escape(w)}\b", corpus_text)]
    whitelist += [p for p in tells.FLAG_PHRASES + tells.WATCH_PHRASES
                  if p in corpus_text]
    if emoji_count / max(len(docs), 1) > 0.3:
        whitelist.append("emoji")
    if ";" in corpus_text:
        whitelist.append(";")

    return {
        "n_messages": len(docs),
        "mean_sentence_len": round(statistics.mean(all_sent_lengths), 1) if all_sent_lengths else 0,
        "sentence_len_std": round(statistics.pstdev(all_sent_lengths), 1) if all_sent_lengths else 0,
        "greetings": greetings.most_common(3),
        "signoffs": signoffs.most_common(3),
        "em_dash_per_msg": round(em_dash / max(len(docs), 1), 2),
        "exclaim_per_msg": round(exclaim / max(len(docs), 1), 2),
        "emoji_per_msg": round(emoji_count / max(len(docs), 1), 2),
        "contraction_rate_per_100w": round(100 * contractions / max(total_words, 1), 1),
        "avg_msg_words": round(total_words / max(len(docs), 1)),
        "pet_phrases": pet_phrases,
        "whitelist": whitelist,
    }


def pick_samples(docs: list, k: int = 6) -> list:
    """Pick diverse few-shot samples: shortest, longest, and mid-length messages."""
    docs = sorted(docs, key=lambda d: len(d.split()))
    if len(docs) <= k:
        return docs
    idxs = [round(i * (len(docs) - 1) / (k - 1)) for i in range(k)]
    return [docs[i] for i in sorted(set(idxs))]


def build_profile() -> str:
    docs = load_corpus()
    if not docs:
        raise SystemExit(
            "No writing samples found in voice/corpus/. Add her exported emails or "
            "messages first - see voice/corpus/README.md. The corpus must be her own "
            "writing, provided by her."
        )
    stats = analyze(docs)
    samples = pick_samples(docs)

    def fmt_counter(pairs):
        return ", ".join(f'"{g}" ({c}x)' for g, c in pairs) or "none detected"

    profile = f"""# Voice profile (measured from {stats['n_messages']} of her own messages)

## Measured habits
- Sentences: mean {stats['mean_sentence_len']} words, std dev {stats['sentence_len_std']} - drafts should keep this variance
- Typical message length: ~{stats['avg_msg_words']} words
- Greetings she uses: {fmt_counter(stats['greetings'])}
- Sign-offs she uses: {fmt_counter(stats['signoffs'])}
- Em dashes per message: {stats['em_dash_per_msg']} | exclamation marks: {stats['exclaim_per_msg']} | emoji: {stats['emoji_per_msg']}
- Contractions per 100 words: {stats['contraction_rate_per_100w']} (match this - don't formalize her)
- Phrases she actually repeats: {', '.join(stats['pet_phrases']) or 'none stood out'}

## Rules for drafting as her
- Match the greeting/sign-off habits above exactly; never invent new ones.
- Keep her rhythm: mix of sentence lengths matching the std dev above.
- Stay at or under her typical message length.
- Use her contractions level. Plain words over fancy ones.
- If a stat above is 0 (em dashes, emoji, semicolons), never use that mark.

## Real samples of her writing (match this voice, not generic professional tone)
""" + "\n".join(f"--- sample {i+1} ---\n{s}\n" for i, s in enumerate(samples))

    VOICE_PROFILE_PATH.write_text(profile)
    (VOICE_DIR / "whitelist.json").write_text(json.dumps(stats["whitelist"], indent=2))
    return profile


def get_profile() -> str:
    if VOICE_PROFILE_PATH.exists():
        return VOICE_PROFILE_PATH.read_text()
    return (
        "# Voice profile\nNo corpus analyzed yet (run: python -m agent voice-build). "
        "Until then: write plainly, short sentences mixed with long, no em dashes, "
        "no corporate phrases, sound like a real person dashing off a note."
    )
