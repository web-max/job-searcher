"""End-to-end pipeline tests with MOCK_LLM=1 (no API key needed)."""
import pytest

from agent import llm, outreach, rank, tracker
from agent.settings import load_profile, load_settings


@pytest.fixture(autouse=True)
def mock_env(tmp_path, monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    monkeypatch.setattr(tracker, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(outreach, "OUTBOX_DIR", tmp_path / "outbox")
    (tmp_path / "outbox").mkdir()


def _seed_jobs(n=3):
    jobs = [{"id": f"j{i}", "source": "test", "company": f"Co{i}",
             "title": "Customer Success Manager", "url": f"https://x.com/{i}",
             "location": "Remote", "description": "SaaS onboarding renewals",
             "posted_at": "2026-07-10", "salary": ""} for i in range(n)]
    tracker.upsert_jobs(jobs)
    return jobs


def test_mock_provider_detected():
    assert llm.provider() == "mock"


def test_rank_with_mock_llm():
    _seed_jobs()
    result = rank.run(load_profile(), load_settings())
    assert result["ranked"] == 3
    for j in tracker.top_jobs(min_score=0, limit=10):
        assert j["score"] >= 70
        assert j["score_reason"]


def test_outreach_draft_written_and_linted():
    _seed_jobs(1)
    path = outreach.draft("info_interview", person="Jane Doe",
                          person_role="CSM", company="Co0", job_id="j0",
                          context="her post about onboarding playbooks")
    content = open(path).read()
    assert "## Message" in content
    assert "Before sending checklist" in content
    assert "checklist" in content.lower()


def test_outreach_unknown_kind_rejected():
    with pytest.raises(SystemExit):
        outreach.draft("cold_pitch_blast")


def test_mock_json_scores_parse():
    user = "JOB abc\nstuff\nJOB def\n"
    data = llm.complete_json("s", user)
    ids = {s["id"] for s in data["scores"]}
    assert ids == {"abc", "def"}
