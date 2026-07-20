"""Minimal YAML-subset loader (flat keys + simple lists) — zero dependencies."""
from __future__ import annotations


def load_config(path: str) -> dict:
    cfg: dict = {}
    current_list = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            if line.startswith("  - ") and current_list is not None:
                item = line.strip()[2:].split("#")[0].strip().strip('"')
                cfg[current_list].append(item)
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                k, v = k.strip(), v.split("#")[0].strip().strip('"')
                if v == "":
                    cfg[k] = []
                    current_list = k
                else:
                    cfg[k] = int(v) if v.isdigit() else v
                    current_list = None
    return cfg


def workdir(cfg: dict, cfg_path: str):
    """Resolve workdir relative to the config file, not the CWD — so the
    pipeline behaves identically wherever it is invoked from."""
    from pathlib import Path
    p = Path(cfg["workdir"])
    return p if p.is_absolute() else (Path(cfg_path).resolve().parent / p).resolve()
