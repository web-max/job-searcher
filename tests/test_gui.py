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
    # mark as onboarded so the wizard gate doesn't redirect page tests
    flag = tmp_path / ".onboarded"
    flag.write_text("done")
    monkeypatch.setattr(gui_app, "ONBOARDED_FLAG", flag)
    monkeypatch.setattr(gui_app, "ENV_PATH", tmp_path / ".env")
    monkeypatch.setattr(gui_app, "PROFILE_PATH", tmp_path / "profile.yaml")
    gui_app.app.config["TESTING"] = True
    return gui_app.app.test_client()


@pytest.fixture()
def fresh_client(tmp_path, monkeypatch):
    """A client that has NOT been onboarded (wizard tests)."""
    monkeypatch.setenv("MOCK_LLM", "1")
    monkeypatch.setattr(tracker, "DB_PATH", tmp_path / "test.db")
    from gui import app as gui_app
    monkeypatch.setattr(gui_app, "OUTBOX_DIR", tmp_path / "outbox")
    (tmp_path / "outbox").mkdir()
    monkeypatch.setattr(gui_app, "ONBOARDED_FLAG", tmp_path / ".onboarded")
    monkeypatch.setattr(gui_app, "ENV_PATH", tmp_path / ".env")
    monkeypatch.setattr(gui_app, "PROFILE_PATH", tmp_path / "profile.yaml")
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


# ---------------------------------------------------------------- onboarding

def test_fresh_user_redirected_to_wizard(fresh_client):
    resp = fresh_client.get("/")
    assert resp.status_code == 302
    assert "/welcome" in resp.headers["Location"]


def test_wizard_pages_render(fresh_client):
    for path in ("/welcome", "/welcome/key", "/welcome/profile",
                 "/welcome/voice", "/welcome/tour"):
        resp = fresh_client.get(path)
        assert resp.status_code == 200, path
        assert b"first-time setup" in resp.data


def test_wizard_key_skip(fresh_client):
    resp = fresh_client.post("/welcome/key", data={"skip": "1"})
    assert resp.status_code == 302
    assert "/welcome/profile" in resp.headers["Location"]


def test_wizard_key_saved_when_valid(fresh_client, monkeypatch, tmp_path):
    from gui import app as gui_app
    monkeypatch.setattr(gui_app, "_test_deepseek_key", lambda k: (True, "ok"))
    resp = fresh_client.post("/welcome/key", data={"key": "sk-test123"})
    assert resp.status_code == 302
    assert "DEEPSEEK_API_KEY=sk-test123" in gui_app.ENV_PATH.read_text()


def test_wizard_key_rejected_when_invalid(fresh_client, monkeypatch):
    from gui import app as gui_app
    monkeypatch.setattr(gui_app, "_test_deepseek_key",
                        lambda k: (False, "the key was rejected"))
    resp = fresh_client.post("/welcome/key", data={"key": "sk-bad"})
    assert resp.status_code == 200
    assert b"didn't work" in resp.data
    assert not gui_app.ENV_PATH.exists()


def test_wizard_profile_saved(fresh_client):
    import yaml
    from gui import app as gui_app
    resp = fresh_client.post("/welcome/profile", data={
        "name": "Jane Test", "location": "Lima", "country": "Peru",
        "timezone": "Peru (UTC-5)", "languages": "Spanish (native), English (fluent)",
        "titles": "Customer Success Manager, Account Manager",
        "seniority": "mid", "remote_only": "true", "salary_floor": "$24,000",
        "summary": "Five years in customer-facing roles.",
        "skills": "onboarding, Salesforce", "dealbreakers": "on-site only"})
    assert resp.status_code == 302
    profile = yaml.safe_load(gui_app.PROFILE_PATH.read_text())
    assert profile["name"] == "Jane Test"
    assert profile["country"] == "Peru"
    assert profile["location"] == "Lima, Peru"
    assert "latam" in profile["eligible_regions"]
    assert "worldwide" in profile["eligible_regions"]
    assert "peru" in profile["eligible_regions"]
    assert profile["languages"] == ["Spanish (native)", "English (fluent)"]
    assert profile["target_titles"] == ["Customer Success Manager", "Account Manager"]
    assert profile["salary_floor_usd"] == 24000
    assert profile["remote_only"] is True


def test_regions_for_country_mapping():
    from gui.app import regions_for_country
    peru = regions_for_country("Peru")
    assert {"worldwide", "anywhere", "peru", "latam"} <= set(peru)
    us = regions_for_country("United States")
    assert "north america" in us and "latam" not in us
    unknown = regions_for_country("Atlantis")
    assert unknown[:2] == ["worldwide", "anywhere"] and "atlantis" in unknown
    assert regions_for_country("") == ["worldwide", "anywhere"]


def test_wizard_profile_requires_essentials(fresh_client):
    resp = fresh_client.post("/welcome/profile", data={"name": "", "titles": "",
                                                       "summary": ""})
    assert resp.status_code == 302
    assert "err=1" in resp.headers["Location"]


def test_wizard_finish_sets_flag_and_unlocks(fresh_client):
    from gui import app as gui_app
    resp = fresh_client.post("/welcome/tour")
    assert resp.status_code == 302
    assert gui_app.ONBOARDED_FLAG.exists()
    resp = fresh_client.get("/")
    assert resp.status_code == 200  # gate lifted


def test_onboarded_user_can_rerun_wizard(client):
    resp = client.get("/welcome")
    assert resp.status_code == 200


# ---------------------------------------------------------------- model switch

def test_model_switch_saved(client, monkeypatch):
    from gui import app as gui_app
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    resp = client.post("/settings/model", data={"model": "deepseek-v4-pro"})
    assert resp.status_code == 302
    assert "DEEPSEEK_MODEL=deepseek-v4-pro" in gui_app.ENV_PATH.read_text()
    import os
    assert os.environ["DEEPSEEK_MODEL"] == "deepseek-v4-pro"


def test_model_switch_rejects_unknown(client, monkeypatch):
    from gui import app as gui_app
    resp = client.post("/settings/model", data={"model": "gpt-99-evil"})
    assert resp.status_code == 302
    assert (not gui_app.ENV_PATH.exists()
            or "gpt-99-evil" not in gui_app.ENV_PATH.read_text())


def test_help_shows_current_model(client, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
    resp = client.get("/help")
    assert b"higher-quality writing" in resp.data


def test_wizard_key_saves_model_choice(fresh_client, monkeypatch):
    from gui import app as gui_app
    monkeypatch.setattr(gui_app, "_test_deepseek_key", lambda k: (True, "ok"))
    resp = fresh_client.post("/welcome/key",
                             data={"key": "sk-test123", "model": "deepseek-v4-pro"})
    assert resp.status_code == 302
    env = gui_app.ENV_PATH.read_text()
    assert "DEEPSEEK_API_KEY=sk-test123" in env
    assert "DEEPSEEK_MODEL=deepseek-v4-pro" in env
