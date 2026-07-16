"""Central place for repo-relative paths so every module agrees on layout."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
PROFILE_PATH = CONFIG_DIR / "profile.yaml"
PROFILE_EXAMPLE_PATH = CONFIG_DIR / "profile.example.yaml"
SETTINGS_PATH = CONFIG_DIR / "settings.yaml"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "tracker.db"
OUTBOX_DIR = ROOT / "outbox"
VOICE_DIR = ROOT / "voice"
VOICE_CORPUS_DIR = VOICE_DIR / "corpus"
VOICE_PROFILE_PATH = VOICE_DIR / "voice_profile.md"
TEMPLATES_DIR = ROOT / "templates" / "outreach"

for d in (DATA_DIR, OUTBOX_DIR, VOICE_CORPUS_DIR):
    d.mkdir(parents=True, exist_ok=True)
