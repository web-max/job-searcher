"""Model resolution tests."""
from agent import llm


def test_env_var_wins(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
    assert llm.deepseek_model() == "deepseek-v4-pro"


def test_settings_file_fallback(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    import agent.settings as s
    monkeypatch.setattr(s, "load_settings",
                        lambda: {"llm": {"deepseek_model": "deepseek-v4-pro"}})
    assert llm.deepseek_model() == "deepseek-v4-pro"


def test_default_when_nothing_configured(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    import agent.settings as s
    monkeypatch.setattr(s, "load_settings", lambda: {})
    assert llm.deepseek_model() == "deepseek-v4-flash"
