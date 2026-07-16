"""GUI smoke tests with Flask's test client (Playwright covers the real browser)."""
import pytest

from agent import tracker


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    monkeypatch.setattr(tracker, "DB_PATH", tmp_path / "test.db")
    from gui import app as gui_app
    monkeypatch.setattr(gui_app, "OUTBOX_DIR", tmp_path / "outbox")
    (tmp_path / "outbox").mkdir()
    gui_app.app.config["TESTING"] = True
    return gui_app.app.test_client()


def _seed():
    tracker.upsert_jobs([{
        "id": "j1", "source": "test", "company": "Acme",
        "title": "Customer Success Manager", "url": "https://x.com/1",
        "location": "Remote", "description": "desc", "posted_at": "2026-07-10",
        "salary": ""}])
    tracker.set_score("j1", 85, "great fit")


@pytest.mark.parametrize("path", ["/", "/jobs", "/outbox", "/outreach", "/people", "/help"])
def test_pages_render(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    assert b"Job Search HQ" in resp.data


def test_job_detail_and_events(client):
    _seed()
    resp = client.get("/job/j1")
    assert b"Customer Success Manager" in resp.data
    resp = client.post("/job/j1/event", data={"event": "applied"})
    assert resp.status_code == 302
    assert tracker.get_job("j1")["status"] == "applied"


def test_outreach_form_posts(client):
    _seed()
    resp = client.post("/outreach", data={
        "kind": "info_interview", "person": "Jane Doe", "person_role": "CSM",
        "company": "Acme", "job": "j1", "context": "her post about churn",
        "channel": "linkedin"})
    assert resp.status_code == 302
    assert tracker.find_contact("Jane Doe") is not None


def test_outbox_traversal_blocked(client):
    resp = client.get("/outbox/..%2F..%2Fetc%2Fpasswd")
    assert resp.status_code in (200, 404)
    assert b"root:" not in resp.data


def test_missing_job_404ish(client):
    resp = client.get("/job/nope")
    assert b"not found" in resp.data.lower()
