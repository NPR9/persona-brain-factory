"""Stage 3 — wiki compilation.

For each cleaned transcript, an LLM extracts material into the configured wiki
categories, appending Obsidian-style markdown with [[wikilinks]]. Long
transcripts are chunked.

Checkpointing is the load-bearing feature: a 300-video corpus WILL crash
mid-run (rate limits, network, laptop sleep). Progress is written to
checkpoint.json after every file; rerunning the same command resumes exactly
where it stopped. Learned the hard way on a 500-transcript build.

DRY_RUN=1 python scripts/03_compile_wiki.py config.yaml   # no API, stub output
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
from _config import load_config, workdir
from providers import complete

SYSTEM = ("You are a knowledge engineer building an Obsidian wiki about one thinker. "
          "From the transcript chunk, extract durable material into the given categories. "
          "Return STRICT JSON only: {\"<Category>\": [\"markdown bullet\", ...], ...}. "
          "Only include categories with real content. Quote sparingly; paraphrase ideas. "
          "Use [[wikilinks]] when referencing other concepts.")


def chunks(text: str, size: int):
    for i in range(0, len(text), size):
        yield text[i:i + size]


def main(cfg_path: str) -> None:
    cfg = load_config(cfg_path)
    dry = os.environ.get("DRY_RUN", "0") == "1"
    work = workdir(cfg, cfg_path)
    cleaned = work / "raw" / "transcripts" / "_cleaned"
    wiki = work / "wiki"
    for cat in cfg["categories"]:
        (wiki / cat).mkdir(parents=True, exist_ok=True)

    ckpt_path = work / cfg["checkpoint_file"]
    done = set(json.loads(ckpt_path.read_text())) if ckpt_path.exists() else set()

    files = sorted(cleaned.glob("*.txt"))
    print(f"{len(files)} transcripts, {len(done)} already done, dry_run={dry}")
    for f in files:
        if f.name in done:
            continue
        text = f.read_text(encoding="utf-8")
        merged: dict[str, list[str]] = {}
        for ch in chunks(text, int(cfg["chunk_chars"])):
            if dry:
                extracted = {cfg["categories"][0]: [f"(dry-run) key idea from {f.stem}"]}
            else:
                raw = complete(cfg["provider"], cfg["model"], SYSTEM,
                               f"TRANSCRIPT: {f.stem}\n\n{ch}")
                raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
                try:
                    extracted = json.loads(raw)
                except json.JSONDecodeError:
                    print(f"  ! unparseable chunk in {f.name}, skipping chunk")
                    continue
                time.sleep(0.5)  # polite pacing
            for cat, items in extracted.items():
                merged.setdefault(cat, []).extend(items)
        for cat, items in merged.items():
            if cat not in cfg["categories"] or not items:
                continue
            page = wiki / cat / f"{f.stem}.md"
            body = f"# {f.stem}\n\n" + "\n".join(f"- {i}" for i in items) + "\n"
            page.write_text(body, encoding="utf-8")
        done.add(f.name)
        ckpt_path.write_text(json.dumps(sorted(done)))
        print(f"  compiled {f.name} -> {len(merged)} categories")
    print("wiki compile complete")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
