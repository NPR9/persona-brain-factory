# persona-brain-factory

A four-stage pipeline that turns any public body of talks into a queryable "persona brain": an Obsidian knowledge wiki plus a distilled system prompt that makes an LLM reason and speak as that thinker.

```
channel URL ─► [1] scrape ─► [2] clean ─► [3] compile wiki ─► [4] synthesize
              yt-dlp VTT     dedupe,      LLM extraction        persona
              captions       strip cues   into categories,      system prompt
                                          [[wikilinks]],        (paste into any
                                          checkpointed          LLM project)
```

> **Provenance.** Generalized from a pipeline I built and ran repeatedly to construct working persona brains from corpora ranging from a few dozen to several hundred transcripts (negotiation, health-science, philosophy, and creative-strategy subjects). This repo ships the factory, not the products.

## BYO-corpus, by design

The factory ships **no corpus and no finished brain**. You point it at material you have the right to process; everything builds locally into `vaults/` (gitignored). Pipeline public, corpus private — that separation is what makes persona-brain work publishable and copyright-clean, and it is a deliberate architectural stance, not an omission.

## Usage

```bash
pip install yt-dlp                       # only external dependency
cp config.example.yaml config.yaml       # set persona, channel, provider, categories
python scripts/01_scrape.py config.yaml
python scripts/02_clean.py  config.yaml
python scripts/03_compile_wiki.py config.yaml     # needs ANTHROPIC_API_KEY or DEEPSEEK_API_KEY
python scripts/04_synthesize.py config.yaml
```

Try the machinery without an API key or corpus:

```bash
DRY_RUN=1 python scripts/03_compile_wiki.py config.yaml
DRY_RUN=1 python scripts/04_synthesize.py config.yaml
```

Output vault opens directly in Obsidian; graph view shows the `[[wikilink]]` mesh. The synthesized `_system_prompt.md` drops into a Claude Project, custom GPT, or local model.

## Design decisions

**Checkpointing is the load-bearing feature.** A 300-video compile *will* die mid-run — rate limits, network, laptop sleep. Progress persists to `checkpoint.json` after every file; rerunning the same command resumes exactly where it stopped. Added after losing hours on a ~500-transcript build; never lost an hour since.

**Provider-agnostic on purpose.** Wiki compilation is a bulk job, and bulk-token economics shift monthly. Anthropic and DeepSeek sit behind one `complete()` interface (stdlib `urllib`, zero SDK dependencies); switching is a config edit.

**Categories are the schema of a mind.** `Principles / Frameworks / Heuristics / Voice / Situations` is a default, not a law — a negotiation brain wants `Tactics` and `Phrases`; a health-science brain wants `Protocols`. Category design is where the operator's judgment enters the pipeline, so it lives in config.

**Wiki first, prompt second.** The wiki is the retrieval layer (upload to project knowledge); the system prompt is the voice. Separating them means the brain can grow — recompile new material into the wiki without touching the persona's identity file.

**Strict-JSON extraction with graceful degradation.** The compiler demands JSON-only responses, strips code fences, and skips unparseable chunks with a logged warning instead of dying — at bulk scale, per-chunk failure tolerance beats per-run fragility.

## License

MIT (pipeline code). Corpora you process remain governed by their own rights.
