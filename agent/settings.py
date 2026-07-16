"""Load profile.yaml and settings.yaml with helpful errors."""
import sys

import yaml

from .paths import PROFILE_PATH, PROFILE_EXAMPLE_PATH, SETTINGS_PATH


def load_settings() -> dict:
    with open(SETTINGS_PATH) as f:
        return yaml.safe_load(f)


def load_profile() -> dict:
    path = PROFILE_PATH if PROFILE_PATH.exists() else PROFILE_EXAMPLE_PATH
    if path is PROFILE_EXAMPLE_PATH:
        print(
            "warning: config/profile.yaml not found, using the EXAMPLE profile. "
            "Copy config/profile.example.yaml to config/profile.yaml and fill it in.",
            file=sys.stderr,
        )
    with open(path) as f:
        return yaml.safe_load(f)


def profile_summary_for_llm(profile: dict) -> str:
    """A compact plain-text rendering of the profile for prompts."""
    lines = [
        f"Name: {profile.get('name')}",
        f"Location: {profile.get('location')} ({profile.get('timezone')})",
        f"Target titles: {', '.join(profile.get('target_titles', []))}",
        f"Seniority: {profile.get('seniority')}",
        f"Remote only: {profile.get('remote_only')}",
        f"Salary floor (USD): {profile.get('salary_floor_usd')}",
        f"Needs visa sponsorship: {profile.get('visa_sponsorship_needed')}",
        f"Background: {profile.get('summary', '').strip()}",
        f"Skills: {', '.join(profile.get('skills', []))}",
        f"Strong matches: {', '.join(profile.get('strong_matches', []))}",
        f"Dealbreakers: {', '.join(profile.get('dealbreakers', []))}",
    ]
    return "\n".join(lines)
