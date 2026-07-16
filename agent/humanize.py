"""Draft linter + rewrite loop for AI tells.

Philosophy (from docs/research/05-ai-writing-tells.md): the failure mode that
kills outreach isn't "detected as AI", it's "detected as generic". So this
module does two jobs:
  1. lint() - mechanical checks for known tells (words, punctuation, structure)
  2. rewrite() - an LLM pass that fixes findings while keeping the sender's voice

Any term in the sender's own corpus whitelist is allowed: the goal is matching
her baseline, not zero usage. We deliberately do NOT chase AI-detector scores.
"""
import json
import re
import statistics

from . import tells
from .paths import VOICE_DIR

WHITELIST_PATH = VOICE_DIR / "whitelist.json"


def _sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def _load_whitelist() -> set:
    if WHITELIST_PATH.exists():
        try:
            return {w.lower() for w in json.loads(WHITELIST_PATH.read_text())}
        except (json.JSONDecodeError, TypeError):
            return set()
    return set()


def lint(text: str, kind: str = "message") -> list:
    """Return a list of findings: {severity, rule, detail}."""
    findings = []
    lower = text.lower()
    whitelist = _load_whitelist()

    def hit(severity, rule, detail):
        findings.append({"severity": severity, "rule": rule, "detail": detail})

    # --- banned / flagged vocabulary
    for p in tells.BAN_PHRASES:
        if p in lower:
            hit("high", "banned-phrase", f'"{p}"')
    for w in tells.FLAG_WORDS:
        if w not in whitelist and re.search(rf"\b{re.escape(w)}\b", lower):
            hit("medium", "flag-word", f'"{w}"')
    for p in tells.FLAG_PHRASES:
        if p not in whitelist and p in lower:
            hit("medium", "flag-phrase", f'"{p}"')
    watch_hits = [w for w in tells.WATCH_WORDS
                  if w not in whitelist and re.search(rf"\b{re.escape(w)}\b", lower)]
    watch_hits += [p for p in tells.WATCH_PHRASES if p not in whitelist and p in lower]
    if len(watch_hits) >= 2:
        hit("low", "watch-words", f"several weak tells co-occur: {watch_hits}")

    # --- punctuation & typography
    em_dashes = text.count("—") + text.count(" - ")
    if "—" in text:
        hit("high", "em-dash", f"{text.count(chr(0x2014))} em dash(es); use a comma, period, or parenthesis")
    if re.search(r"[“”‘’]", text):
        hit("medium", "curly-quotes", "smart quotes suggest pasted LLM output; use straight quotes")
    if re.search(r"\*\*|^#{1,6}\s|^\s*[-*]\s", text, re.M) and kind != "notes":
        hit("high", "markdown-artifacts", "markdown formatting in a plain-text message")
    if re.search(r"[\U0001F300-\U0001FAFF]", text) and "emoji" not in whitelist:
        hit("medium", "emoji", "emoji present; only keep if she actually uses them")
    if text.count(";") > 0 and ";" not in whitelist:
        hit("low", "semicolon", "most people never use semicolons in messages")

    # --- structural tells
    if re.search(r"\b(not|isn'?t|aren'?t|wasn'?t) (just|only|merely|about)\b[^.!?]{0,80}"
                 r"\b(but|it'?s|they'?re|this is)\b", lower):
        hit("high", "contrastive-negation", '"not just X, (but) Y" construction - the most damning tell')
    triads = re.findall(r"\b\w+, \w+,? and \w+\b", text)
    if len(triads) > 1:
        hit("medium", "rule-of-three", f"{len(triads)} triads; keep at most one: {triads}")
    if re.search(r",\s+(highlighting|ensuring|underscoring|reflecting|showcasing|demonstrating|emphasizing)\b", lower):
        hit("medium", "ing-tail", "sentence ends in an '-ing' analysis tail")
    for opener in ("i hope you", "i trust you", "i was so impressed", "i admire your incredible"):
        if lower.lstrip().startswith(opener):
            hit("medium", "pleasantry-opener", "first sentence should contain a specific detail, not a pleasantry")

    # --- rhythm
    sents = _sentences(text)
    if len(sents) >= 4:
        lengths = [len(s.split()) for s in sents]
        if statistics.pstdev(lengths) < 3.5:
            hit("medium", "uniform-rhythm",
                f"sentence lengths too uniform ({lengths}); mix short and long")

    # --- content checks (heuristic)
    if re.search(r"\b(studies show|experts (say|agree|argue)|industry reports)\b", lower):
        hit("medium", "vague-attribution", "unattributed 'studies show' style claim")
    if re.search(r"\[(?!\d)[^\]]{2,30}\]|\{[^}]{2,30}\}", text):
        hit("high", "placeholder", "unfilled placeholder bracket left in draft")
    if re.search(r"let me know if (you'?re )?interested", lower):
        hit("medium", "weak-cta", 'replace "let me know if interested" with a concrete, single-question ask')

    # --- length norms by message type
    words = len(text.split())
    limits = {"linkedin_note": 60, "linkedin_message": 110, "email": 130, "cover_note": 260}
    limit = limits.get(kind)
    if limit and words > limit:
        hit("medium", "too-long", f"{words} words; {kind} should be under ~{limit}")

    return findings


def format_findings(findings: list) -> str:
    if not findings:
        return "clean: no tells found"
    return "\n".join(f"  [{f['severity']:^6}] {f['rule']}: {f['detail']}" for f in findings)


def blocking(findings: list, fail_on=("high",)) -> bool:
    return any(f["severity"] in fail_on for f in findings)


REWRITE_SYSTEM = """You edit drafts of short job-search messages so they read like the
real person wrote them. You receive: the draft, a list of specific problems found by a
linter, and the sender's voice profile. Fix ONLY the flagged problems plus anything that
sounds like a language model wrote it. Keep the message's facts, ask, and length. Keep
the sender's voice: her greeting and sign-off habits, her rhythm, her level of casualness.
Plain words. Vary sentence length. No em dashes. Never use "not just X, but Y"
constructions. Do not add new claims or compliments. Return only the rewritten message,
no commentary."""


def rewrite(text: str, findings: list, voice_profile: str, kind: str = "message") -> str:
    from . import llm
    user = (
        f"VOICE PROFILE:\n{voice_profile}\n\n"
        f"MESSAGE TYPE: {kind}\n\n"
        f"LINTER FINDINGS:\n{format_findings(findings)}\n\n"
        f"DRAFT:\n{text}"
    )
    return llm.complete(REWRITE_SYSTEM, user, max_tokens=800, temperature=0.6).strip()


def polish(text: str, voice_profile: str, kind: str = "message",
           max_passes: int = 2, fail_on=("high",)):
    """Lint -> rewrite loop. Returns (final_text, final_findings, passed)."""
    current = text
    for _ in range(max_passes):
        findings = lint(current, kind)
        if not blocking(findings, fail_on):
            return current, findings, True
        current = rewrite(current, findings, voice_profile, kind)
    findings = lint(current, kind)
    return current, findings, not blocking(findings, fail_on)
