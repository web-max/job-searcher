"""Voice profile builder tests using a synthetic corpus."""
import json

import pytest

from agent import voice
from agent.paths import VOICE_CORPUS_DIR, VOICE_PROFILE_PATH, VOICE_DIR

SYNTHETIC = """Hi Sara!
Just wanted to say thanks again for covering my shift on Tuesday. You're a lifesaver. I owe you a coffee, seriously.
Talk soon,
Jane
---
Hey Mom,
The apartment hunt is going ok. We saw two places this weekend and one actually had a real kitchen, which felt like a miracle. Will call you Sunday.
Love you!
---
Hi Mr. Alvarez,
Thanks for sending the contract over. I read through it and just have one question about the deposit timing. Could we do the 15th instead of the 1st? Everything else looks good to me.
Thanks so much,
Jane
---
Hey! Sorry for the slow reply, this week got away from me. Yes to Saturday. I'll bring the good snacks.
---
Hi Dr. Patel,
I need to reschedule Thursday's appointment. Something came up at work and I can't get out in time. Do you have anything early next week? Mornings are best for me.
Thank you!
Jane
"""


@pytest.fixture()
def corpus(tmp_path, monkeypatch):
    # redirect corpus + outputs into tmp to avoid touching the real folders
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "samples.txt").write_text(SYNTHETIC)
    monkeypatch.setattr(voice, "VOICE_CORPUS_DIR", corpus_dir)
    monkeypatch.setattr(voice, "VOICE_PROFILE_PATH", tmp_path / "voice_profile.md")
    monkeypatch.setattr(voice, "VOICE_DIR", tmp_path)
    return tmp_path


def test_load_corpus_splits_messages(corpus):
    docs = voice.load_corpus()
    assert len(docs) == 5


def test_analyze_extracts_habits(corpus):
    stats = voice.analyze(voice.load_corpus())
    assert stats["n_messages"] == 5
    greetings = dict(stats["greetings"])
    assert "hi" in greetings or "hey" in greetings
    signoffs = dict(stats["signoffs"])
    assert any(s in signoffs for s in ("thanks so much", "thank you", "talk soon"))
    assert stats["mean_sentence_len"] > 0
    assert stats["exclaim_per_msg"] > 0  # she uses exclamation marks


def test_build_profile_writes_outputs(corpus):
    profile = voice.build_profile()
    assert "Voice profile" in profile
    assert (corpus / "voice_profile.md").exists()
    whitelist = json.loads((corpus / "whitelist.json").read_text())
    assert isinstance(whitelist, list)


def test_empty_corpus_exits(tmp_path, monkeypatch):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(voice, "VOICE_CORPUS_DIR", empty)
    with pytest.raises(SystemExit):
        voice.build_profile()


def test_quoted_reply_stripped():
    body = "Sounds good, see you then!\n\nOn Tue, Jul 1, 2026 John wrote:\n> blah blah"
    assert "blah" not in voice._clean_body(body)
