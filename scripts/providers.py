"""Thin, dependency-free LLM client. Two providers, one interface.

Provider-agnostic by design: wiki compilation is a bulk job (hundreds of
transcripts), and bulk-job economics change monthly. Swapping provider is a
config edit, not a rewrite.
"""
from __future__ import annotations
import json, os, urllib.request

ENDPOINTS = {
    "anthropic": ("https://api.anthropic.com/v1/messages", "ANTHROPIC_API_KEY"),
    "deepseek": ("https://api.deepseek.com/chat/completions", "DEEPSEEK_API_KEY"),
}


def complete(provider: str, model: str, system: str, user: str, max_tokens: int = 2000) -> str:
    url, key_env = ENDPOINTS[provider]
    key = os.environ.get(key_env)
    if not key:
        raise EnvironmentError(f"{key_env} not set")
    if provider == "anthropic":
        body = {"model": model, "max_tokens": max_tokens, "system": system,
                "messages": [{"role": "user", "content": user}]}
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
    else:  # deepseek (OpenAI-compatible)
        body = {"model": model, "max_tokens": max_tokens,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}]}
        headers = {"Authorization": f"Bearer {key}", "content-type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    if provider == "anthropic":
        return "".join(b.get("text", "") for b in data.get("content", []))
    return data["choices"][0]["message"]["content"]
