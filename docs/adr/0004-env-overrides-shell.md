# 4. `.env` overrides shell environment

Date: 2026-10-27
Status: Accepted

## Context

A stale `export LLM_MODEL_NAME=...` in the shell silently won over `.env`, so the wrong (slower) model was used.

## Decision

`main.py` calls `load_dotenv(override=True)`. `.env` is the source of truth for local runs. Config is read once into an `LLMConfig` (`config.py`); `LLM_TOKEN` takes precedence over `LLM_API_KEY`.

## Consequences

- Predictable local behaviour.
- To override per run, edit `.env` or (later) use a CLI flag such as `--model`; shell exports won't work for keys present in `.env`.
