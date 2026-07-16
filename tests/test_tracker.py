"""Tracker DB tests against a temp database."""
import pytest

from agent import tracker


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(tracker, "DB_PATH", tmp_path / "test.db")


def _job(i="abc123", title="CS Manager"):
    return {"id": i, "source": "test", "company": "Acme", "title": title,
            "url": f"https://x.com/{i}", "location": "Remote", "description": "desc",
            "posted_at": "2026-07-10", "salary": ""}


def test_upsert_idempotent():
    assert tracker.upsert_jobs([_job()]) == 1
    assert tracker.upsert_jobs([_job()]) == 0  # second time: no new rows


def test_score_and_top_jobs():
    tracker.upsert_jobs([_job("a1"), _job("a2", "Sales Rep")])
    tracker.set_score("a1", 88, "strong fit")
    tracker.set_score("a2", 40, "wrong field")
    top = tracker.top_jobs(min_score=65)
    assert [j["id"] for j in top] == ["a1"]
    assert tracker.unranked_jobs() == []


def test_status_flow_and_events():
    tracker.upsert_jobs([_job("a1")])
    tracker.log_event("applied", job_id="a1")
    assert tracker.get_job("a1")["status"] == "applied"
    assert tracker.counts_today()["applied"] == 1


def test_contacts_and_followups():
    cid = tracker.add_contact("Jane Doe", company="Acme", role="CSM")
    tracker.log_event("messaged", contact_id=cid)
    assert tracker.find_contact("jane")["status"] == "messaged"
    # not due yet (just messaged)
    assert tracker.followups_due(after_days=6) == []
    # due if threshold is 0 days
    due = tracker.followups_due(after_days=0)
    assert len(due) == 1
    # replied contacts drop out
    tracker.log_event("replied", contact_id=cid)
    assert tracker.followups_due(after_days=0) == []


def test_max_followups_respected():
    cid = tracker.add_contact("Bob")
    tracker.log_event("messaged", contact_id=cid)
    tracker.log_event("followed_up", contact_id=cid)
    tracker.log_event("followed_up", contact_id=cid)
    assert tracker.followups_due(after_days=0, max_followups=2) == []
