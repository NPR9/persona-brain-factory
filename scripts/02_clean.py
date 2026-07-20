"""Stage 2 — VTT cleaning.

Auto-captions arrive as VTT with timestamps, cue settings, and heavy line
repetition (rolling captions duplicate every line 2-3x). Output: one plain
.txt per video, deduplicated, readable.

Usage: python scripts/02_clean.py config.yaml
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from _config import load_config, workdir

TS = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> ")
TAG = re.compile(r"<[^>]+>")


def clean_vtt(text: str) -> str:
    out, prev = [], None
    for line in text.splitlines():
        line = line.strip()
        if (not line or line == "WEBVTT" or TS.match(line)
                or line.startswith(("Kind:", "Language:", "NOTE"))):
            continue
        line = TAG.sub("", line)
        if line and line != prev:
            out.append(line)
            prev = line
    return "\n".join(out)


def main(cfg_path: str) -> None:
    cfg = load_config(cfg_path)
    raw = workdir(cfg, cfg_path) / "raw" / "transcripts"
    cleaned = raw / "_cleaned"
    cleaned.mkdir(parents=True, exist_ok=True)
    n = 0
    for vtt in sorted(raw.glob("*.vtt")):
        txt = clean_vtt(vtt.read_text(encoding="utf-8", errors="ignore"))
        if len(txt) < 200:      # empty / no-caption videos
            continue
        (cleaned / (vtt.stem.replace(".en", "") + ".txt")).write_text(txt, encoding="utf-8")
        n += 1
    print(f"cleaned {n} transcripts -> {cleaned}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
