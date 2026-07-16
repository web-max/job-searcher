"""Assisted apply: gating, LinkedIn block, field mapping. No browser needed."""
import pytest

from agent import apply


PROFILE = {
    "name": "Jane Example",
    "location": "Lima, Peru",
    "links": {"linkedin": "https://linkedin.com/in/janeexample", "portfolio": ""},
    "contact": {"email": "jane@example.com", "phone": "+51 900 000 000",
                "resume_path": "/tmp/resume.pdf"},
}


def _field(idx, kind="text", **kw):
    f = {"idx": idx, "kind": kind, "type": kind, "name": "", "id": "",
         "label": "", "placeholder": "", "autocomplete": ""}
    f.update(kw)
    return f


# ------------------------------------------------------------------ gating

def test_autofill_off_by_default(monkeypatch):
    monkeypatch.delenv("FORM_AUTOFILL", raising=False)
    assert apply.autofill_enabled({}) is False
    assert apply.autofill_enabled({"apply": {"form_autofill": False}}) is False


def test_autofill_on_via_settings(monkeypatch):
    monkeypatch.delenv("FORM_AUTOFILL", raising=False)
    assert apply.autofill_enabled({"apply": {"form_autofill": True}}) is True


def test_env_overrides_settings_both_ways(monkeypatch):
    monkeypatch.setenv("FORM_AUTOFILL", "0")
    assert apply.autofill_enabled({"apply": {"form_autofill": True}}) is False
    monkeypatch.setenv("FORM_AUTOFILL", "1")
    assert apply.autofill_enabled({"apply": {"form_autofill": False}}) is True


# ------------------------------------------------------------------ hard blocks

@pytest.mark.parametrize("url", [
    "https://www.linkedin.com/jobs/view/123",
    "https://linkedin.com/jobs/view/123",
])
def test_linkedin_always_blocked(url):
    assert apply.blocked_reason(url) is not None


def test_non_linkedin_not_blocked():
    assert apply.blocked_reason("https://boards.greenhouse.io/acme/jobs/1") is None
    # substring is not enough - must be the actual host
    assert apply.blocked_reason("https://notlinkedin.com.evil.example/x") is None


def test_known_ats_detection():
    assert apply.is_known_ats("https://boards.greenhouse.io/acme/jobs/1")
    assert apply.is_known_ats("https://jobs.lever.co/acme/1")
    assert apply.is_known_ats("https://jobs.ashbyhq.com/acme/1")
    assert not apply.is_known_ats("https://weworkremotely.com/remote-jobs/x")


# ------------------------------------------------------------------ field mapping

def test_plan_fill_standard_fields():
    fields = [
        _field("agent-0", name="first_name", label="First name"),
        _field("agent-1", name="last_name", label="Last name"),
        _field("agent-2", type="email", name="email", label="Email"),
        _field("agent-3", type="tel", name="phone", label="Phone"),
        _field("agent-4", name="urls[LinkedIn]", label="LinkedIn URL"),
        _field("agent-5", kind="textarea", name="cover_letter", label="Cover letter"),
    ]
    plan, skipped = apply.plan_fill(fields, PROFILE, cover_note="Dear team, hi.")
    got = {f["idx"]: v for f, v in plan}
    assert got["agent-0"] == "Jane"
    assert got["agent-1"] == "Example"
    assert got["agent-2"] == "jane@example.com"
    assert got["agent-3"] == "+51 900 000 000"
    assert got["agent-4"] == "https://linkedin.com/in/janeexample"
    assert got["agent-5"] == "Dear team, hi."
    assert not skipped


def test_plan_fill_never_answers_judgment_questions():
    fields = [
        _field("agent-0", name="gender", label="Gender identity"),
        _field("agent-1", name="veteran_status", label="Veteran status"),
        _field("agent-2", name="salary", label="Desired salary"),
        _field("agent-3", kind="textarea", name="visa", label="Do you need sponsorship?"),
    ]
    plan, skipped = apply.plan_fill(fields, PROFILE, cover_note="note")
    assert plan == []
    assert len(skipped) == 4


def test_plan_fill_resume_upload_only_with_path():
    fields = [_field("agent-0", kind="file", name="resume", label="Resume/CV")]
    plan, _ = apply.plan_fill(fields, PROFILE)
    assert plan == [(fields[0], "/tmp/resume.pdf")]
    no_resume = dict(PROFILE, contact={"email": "jane@example.com"})
    plan, skipped = apply.plan_fill(fields, no_resume)
    assert plan == [] and len(skipped) == 1


def test_plan_fill_unknown_field_left_blank():
    fields = [_field("agent-0", name="favorite_dinosaur", label="Favorite dinosaur")]
    plan, skipped = apply.plan_fill(fields, PROFILE)
    assert plan == [] and len(skipped) == 1


# ------------------------------------------------------------------ cover note

def test_latest_cover_note_extracted(tmp_path, monkeypatch):
    monkeypatch.setattr(apply, "OUTBOX_DIR", tmp_path)
    (tmp_path / "20260101-0000-tailor-abc123.md").write_text(
        "# Application kit\n\n## Cover note\n\nHi team,\nI am Jane.\n\n"
        "## Linter findings on the cover note\n  none\n")
    assert apply.latest_cover_note("abc123") == "Hi team,\nI am Jane."
    assert apply.latest_cover_note("zzz999") == ""
