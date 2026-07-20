"""Stage 4 — persona synthesis.

Reads the entire compiled wiki and produces <persona>_system_prompt.md — the
distilled brain, ready to paste into a Claude Project / custom GPT / local
model system prompt. The wiki is the retrieval layer; this file is the voice.

DRY_RUN=1 supported (assembles a structural stub without API calls).
"""
from __future__ import annotations
import os, sys
from pathlib import Path
from _config import load_config, workdir
from providers import complete

SYSTEM = ("You write system prompts that make an LLM speak and reason as a specific thinker. "
          "From the wiki digest, produce a complete system prompt: identity, core principles, "
          "reasoning style, voice register with signature phrasing patterns, what this thinker "
          "would refuse or push back on, and 3 short example exchanges. Markdown.")


def main(cfg_path: str) -> None:
    cfg = load_config(cfg_path)
    work = workdir(cfg, cfg_path)
    wiki = work / "wiki"
    digest_parts = []
    for cat in cfg["categories"]:
        pages = sorted((wiki / cat).glob("*.md"))
        joined = "\n".join(p.read_text(encoding="utf-8") for p in pages)[:20000]
        digest_parts.append(f"## {cat}\n{joined}")
    digest = "\n\n".join(digest_parts)

    if os.environ.get("DRY_RUN", "0") == "1":
        prompt = (f"# {cfg['persona_name']} — system prompt (dry-run stub)\n\n"
                  f"Digest assembled from {sum(1 for _ in wiki.rglob('*.md'))} wiki pages. "
                  "Run without DRY_RUN to synthesize.")
    else:
        prompt = complete(cfg["provider"], cfg["model"], SYSTEM,
                          f"PERSONA: {cfg['persona_name']}\n\nWIKI DIGEST:\n{digest}",
                          max_tokens=4000)
    out = work / f"{cfg['persona_name']}_system_prompt.md"
    out.write_text(prompt, encoding="utf-8")
    print(f"system prompt written: {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
