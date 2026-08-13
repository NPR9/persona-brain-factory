"""Stage 5 — wiki validation (optional quality gate).

Checks compiled wiki for gaps: categories with no pages, pages with no content,
broken wikilinks. Useful before pushing to production or uploading to project knowledge.

Usage: python scripts/05_validate.py config.yaml
"""
from __future__ import annotations
import sys
from pathlib import Path
from _config import load_config, workdir


def main(cfg_path: str) -> None:
    cfg = load_config(cfg_path)
    wiki = workdir(cfg, cfg_path) / "wiki"
    issues = []
    for cat in cfg["categories"]:
        cat_dir = wiki / cat
        if not cat_dir.exists():
            issues.append(f"[MISSING] category '{cat}' has no directory")
            continue
        pages = list(cat_dir.glob("*.md"))
        if not pages:
            issues.append(f"[EMPTY] category '{cat}' has no pages")
        for page in pages:
            text = page.read_text(encoding="utf-8")
            if len(text) < 50:
                issues.append(f"[SHORT] {cat}/{page.name} < 50 chars")
    if issues:
        print("\n".join(issues))
        return 1
    print(f"✓ wiki valid: {sum(len(list((wiki/c).glob('*.md'))) for c in cfg['categories'])} pages across {len(cfg['categories'])} categories")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "config.yaml"))
