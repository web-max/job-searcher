"""Linter tests: known AI slop must be flagged; genuinely human notes must pass."""
import pytest

from agent import humanize

AI_SLOP_SAMPLES = [
    # classic AI cover-letter opener
    ("I hope this message finds you well. I am writing to express my strong interest "
     "in the Customer Success Manager role at your esteemed organization. I bring a "
     "unique blend of skills, passion, and dedication.",
     ["banned-phrase"]),
    # contrastive negation + em dash
    ("Customer success isn't just about retention — it's about building relationships "
     "that last. I'd love to connect and explore synergies.",
     ["contrastive-negation", "em-dash"]),
    # flag vocabulary pileup
    ("I spearheaded a robust, seamless onboarding overhaul, leveraging cross-functional "
     "synergy to foster meticulous alignment across stakeholders.",
     ["flag-word"]),
    # -ing analysis tail + summary closer
    ("I led the renewal program, ensuring seamless collaboration across teams. "
     "In conclusion, I would be a great fit for this role.",
     ["ing-tail", "banned-phrase"]),
    # placeholder left in draft
    ("Hi Sarah, I saw the posting for [Job Title] and think my background in "
     "[relevant field] would be a great match.",
     ["placeholder"]),
    # weak CTA
    ("Hi Tom, great to connect. I have five years of CS experience. "
     "Let me know if you're interested in chatting.",
     ["weak-cta"]),
    # pick your brain
    ("Hi Dana, I'd love to pick your brain about your career path sometime.",
     ["banned-phrase"]),
]

HUMAN_SAMPLES = [
    "Hi Priya! Saw your post about the Gainsight migration going sideways. We hit the "
    "same wall at my last job and ended up rolling half of it back. Would you have 15 "
    "minutes some morning next week? I'm weighing a move into a CS ops role and your "
    "take would help a lot.\nThanks!\nJane",

    "Hey Marcus, congrats on the new gig at Loom. That's awesome. No agenda here, just "
    "glad to see the news. If you're ever up for a quick catch-up I'd love to hear how "
    "the first month's going.",

    "Hi Ana, I applied for the onboarding specialist role yesterday (req 4482). Quick "
    "context since I know these get buried: I ran onboarding for 40+ mid-market "
    "accounts at Fern and kept churn under 4%. Is there anything else useful I can "
    "send your way?",
]


@pytest.mark.parametrize("text,expected_rules", AI_SLOP_SAMPLES)
def test_ai_slop_is_flagged(text, expected_rules):
    findings = humanize.lint(text, kind="linkedin_message")
    rules = {f["rule"] for f in findings}
    for expected in expected_rules:
        assert expected in rules, f"expected rule '{expected}' in {rules} for: {text[:60]}"


@pytest.mark.parametrize("text", HUMAN_SAMPLES)
def test_human_writing_passes(text):
    findings = humanize.lint(text, kind="linkedin_message")
    high = [f for f in findings if f["severity"] == "high"]
    assert not high, f"false positive on human text: {high}"


def test_blocking_logic():
    findings = [{"severity": "high", "rule": "x", "detail": ""}]
    assert humanize.blocking(findings)
    findings = [{"severity": "low", "rule": "x", "detail": ""}]
    assert not humanize.blocking(findings)
    assert humanize.blocking(findings, fail_on=("high", "medium", "low"))


def test_uniform_rhythm_detected():
    # five sentences of nearly identical, LLM-typical length (~14 words each)
    text = ("The team builds modern tools that help sales people work much more "
            "efficiently today. The product gives every account manager clear "
            "visibility into deals that need attention now. The company culture "
            "truly values remote work and flexible schedules for every employee "
            "there. The role focuses on customer growth outcomes and long term "
            "retention across all accounts. The mission speaks directly to my own "
            "background in customer success and renewals.")
    rules = {f["rule"] for f in humanize.lint(text)}
    assert "uniform-rhythm" in rules


def test_short_sentence_writer_not_penalized():
    # casual, punchy human note: short sentences are her style, not a tell
    text = ("Hi Sarah, thanks for the coffee yesterday. Really helpful to hear "
            "about the team. I'll send that intro this week. Happy to return the "
            "favor anytime. No worries either way.")
    rules = {f["rule"] for f in humanize.lint(text)}
    assert "uniform-rhythm" not in rules


def test_less_about_more_about_variant():
    text = ("Great product work is less about shipping features and more about "
            "understanding why users leave in the first place.")
    findings = humanize.lint(text)
    assert any(f["rule"] == "contrastive-negation" and f["severity"] == "high"
               for f in findings)


def test_cross_sentence_contrastive():
    text = "This isn't just a job. It's the team I have wanted to join for years."
    findings = humanize.lint(text)
    assert any(f["rule"] == "contrastive-negation" for f in findings)


def test_curly_apostrophes_normalized():
    text = "This isn’t just another role, it’s the one I want."
    rules = {f["rule"] for f in humanize.lint(text)}
    assert "contrastive-negation" in rules  # curly quotes must not dodge the regex
    assert "curly-quotes" in rules


def test_greeting_does_not_hide_flattery_opener():
    text = ("Hi Jordan, I was so impressed by your incredible journey through the "
            "industry. Your leadership is truly inspiring to everyone watching.")
    findings = humanize.lint(text)
    rules = {f["rule"] for f in findings}
    assert "flag-phrase" in rules or "pleasantry-opener" in rules


def test_flag_pileup_escalates():
    text = ("I spearheaded a robust rollout, then moved to leverage our tooling to "
            "foster adoption and delve into seamless workflows for the team there.")
    findings = humanize.lint(text)
    assert any(f["rule"] == "flag-pileup" and f["severity"] == "high" for f in findings)


def test_dash_surrogates_flagged():
    text = ("I saw the role - it looks like a great fit - and I wanted to reach "
            "out directly about it.")
    rules = {f["rule"] for f in humanize.lint(text)}
    assert "dash-surrogate" in rules


def test_three_mediums_block():
    findings = [{"severity": "medium", "rule": f"r{i}", "detail": ""} for i in range(3)]
    assert humanize.blocking(findings)
    assert not humanize.blocking(findings[:2])


def test_too_long_flagged():
    text = "word " * 200
    rules = {f["rule"] for f in humanize.lint(text, kind="linkedin_note")}
    assert "too-long" in rules


def test_format_findings_clean():
    assert "clean" in humanize.format_findings([])
