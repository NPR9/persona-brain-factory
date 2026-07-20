"""Stage 1 — corpus acquisition (BYO-corpus).

Downloads auto-captions only (VTT), never media, from a channel URL the user
supplies. The factory ships no corpus: you point it at material you have the
right to process, it builds the brain locally. That line — pipeline public,
corpus private — is what makes a persona-brain project publishable at all.

Usage: python scripts/01_scrape.py config.yaml
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
from _config import load_config, workdir


def main(cfg_path: str) -> None:
    cfg = load_config(cfg_path)
    out = workdir(cfg, cfg_path) / "raw" / "transcripts"
    out.mkdir(parents=True, exist_ok=True)
    cmd = ["yt-dlp", "--write-auto-sub", "--sub-lang", "en", "--skip-download",
           "--output", str(out / "%(title)s.%(ext)s"), cfg["channel_url"]]
    print("running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    n = len(list(out.glob("*.vtt")))
    print(f"done — {n} transcript files in {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
