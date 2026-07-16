"""Minimal multi-provider LLM client.

Providers, in order of preference based on which API key is set:
  - DeepSeek  (DEEPSEEK_API_KEY)  -> OpenAI-compatible, https://api.deepseek.com
  - Anthropic (ANTHROPIC_API_KEY) -> Messages API
  - OpenAI    (OPENAI_API_KEY)    -> chat completions

Only `requests` is needed; no provider SDKs. If no key is set, calls raise a
clear error telling the operator (a human, or Claude Code piloting the repo)
what to do — when Claude Code pilots the repo it does the LLM steps itself and
never needs this module.
"""
import json
import os
import time

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class LLMError(RuntimeError):
    pass


def deepseek_model() -> str:
    """Model resolution: DEEPSEEK_MODEL env var > config/settings.yaml llm section
    > deepseek-v4-flash. (deepseek-chat is deprecated as of 2026-07-24.)"""
    env = os.getenv("DEEPSEEK_MODEL")
    if env:
        return env
    try:
        from .settings import load_settings
        configured = (load_settings().get("llm") or {}).get("deepseek_model")
        if configured:
            return configured
    except Exception:
        pass
    return "deepseek-v4-flash"


def provider() -> str:
    if os.getenv("MOCK_LLM"):
        return "mock"
    if os.getenv("DEEPSEEK_API_KEY"):
        return "deepseek"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    raise LLMError(
        "No LLM API key found. Set DEEPSEEK_API_KEY (or ANTHROPIC_API_KEY / "
        "OPENAI_API_KEY) in .env — see .env.example. If you're piloting this repo "
        "with Claude Code, do this step yourself instead of calling the API."
    )


def _post(url: str, headers: dict, payload: dict, retries: int = 3) -> dict:
    delay = 2.0
    for attempt in range(retries + 1):
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in (429, 500, 502, 503, 529) and attempt < retries:
            time.sleep(delay)
            delay *= 2
            continue
        raise LLMError(f"LLM API error {resp.status_code}: {resp.text[:500]}")
    raise LLMError("unreachable")


def _mock_complete(system: str, user: str) -> str:
    """Deterministic canned output for tests and key-less demos (MOCK_LLM=1).

    If the prompt looks like a ranking request, emit valid scores for every
    JOB <id> found in it; otherwise return a plausible short draft.
    """
    import re

    ids = re.findall(r"^JOB (\w+)$", user, re.M)
    if ids:
        scores = [{"id": i, "score": 70 + (idx % 3) * 9, "reason": "mock score (MOCK_LLM=1)"}
                  for idx, i in enumerate(ids)]
        return json.dumps({"scores": scores})
    return (
        "Hi there, this is a mock draft because MOCK_LLM=1 is set. It stands in for "
        "a real model reply so the pipeline can be tested without an API key. Short "
        "sentence here. Then a much longer one that varies the rhythm enough to keep "
        "the linter's uniformity check quiet during tests. Want to grab 15 minutes "
        "next week?\nThanks!"
    )


def complete(system: str, user: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
    """One-shot completion. Returns the assistant text.

    Prompt-caching note: DeepSeek context caching is automatic on repeated
    prompt prefixes (cache hits bill ~50x cheaper), so callers keep the stable
    parts (system prompt, profile, voice profile) FIRST and the per-item parts
    last. All prompts in this repo are already shaped that way.
    """
    prov = provider()
    if prov == "mock":
        return _mock_complete(system, user)
    if prov == "anthropic":
        data = _post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            payload={
                "model": os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        return "".join(b.get("text", "") for b in data["content"])

    if prov == "deepseek":
        base, key = "https://api.deepseek.com", os.environ["DEEPSEEK_API_KEY"]
        model = deepseek_model()
    else:
        base, key = "https://api.openai.com", os.environ["OPENAI_API_KEY"]
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    data = _post(
        f"{base}/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
        payload={
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
    )
    return data["choices"][0]["message"]["content"]


def complete_json(system: str, user: str, max_tokens: int = 3000):
    """Completion that must return JSON. Strips code fences, retries once on bad JSON."""
    sys_prompt = system + "\nRespond with valid JSON only. No prose, no code fences."
    text = complete(sys_prompt, user, max_tokens=max_tokens, temperature=0.2)
    for attempt in range(2):
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
            cleaned = cleaned.rsplit("```", 1)[0]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if attempt == 0:
                text = complete(
                    sys_prompt,
                    user + "\n\nYour previous reply was not valid JSON. Return ONLY valid JSON.",
                    max_tokens=max_tokens,
                    temperature=0.0,
                )
            else:
                raise LLMError(f"Model returned unparseable JSON: {text[:300]}")
