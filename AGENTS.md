# AGENTS.md

Guidance for coding agents working in this repo.

## Project

CrewAI multi-agent PoC using a local LLM via LM Studio (OpenAI-compatible). A user-supplied topic flows through the Architect, Developer and QA agents in sequence, producing `output/design_doc.md`, `output/Dockerfile` and `output/security_report.md`.

## Commands

- Install: `poetry install`
- Run: `poetry run agents list` / `poetry run agents run <pipeline> ...` (requires LM Studio at `LLM_BASE_URL`)
- Score: `poetry run score-audit <report.md>`; OpenCode benchmark: `scripts/bench_opencode.sh [model]` (slow, 5–25 min/model)
- Test: `poetry run pytest` (no LLM needed)
- Lint: `poetry run ruff check src tests`

## Layout

- `opencode.json`, `.opencode/agent/`, `.opencode/command/`: OpenCode + LM Studio track (`/audit`)

- `src/agent_framework/main.py`: CLI (`agents`, `run-agents` alias)
- `src/agent_framework/pipelines.yaml` + `registry.py`: pipeline definitions (ADR 0006)
- `src/agent_framework/project.py`: inlines a target project's files
- `src/agent_framework/scoring.py`: `score-audit`
- `src/agent_framework/engine.py`: `AgenticEngine`, env setup, task chaining, `Crew` kickoff
- `src/agent_framework/agents.py`: `AgentFactory.create(step)`
- `src/agent_framework/tasks.py`: `TaskFactory.create(step, agent, context)`
- `src/agent_framework/config.py`: `LLMConfig`, `load_llm_config` (`LLM_TOKEN` > `LLM_API_KEY`)
- `tests/`: pytest suite
- `output/`: generated artifacts (gitignored)

## Conventions

- New use cases = new pipeline in `pipelines.yaml` (steps + `context`), not new Python.
- Placeholders: `{topic}` or `{project_name}`/`{project_files}`, filled by `crew.kickoff(inputs=...)`.
- Record benchmark runs in `docs/TEST_RESULTS.md`.
- Agents have no tools; each task's final answer is saved via `Task(output_file=...)` into the per-run folder (ADR 0003).
- Model strings use the LiteLLM form `openai/<model>`.
- Agents get an explicit `crewai.LLM` built from `LLMConfig`; `engine.py` also sets `OPENAI_API_BASE`/`OPENAI_API_KEY` for CrewAI internals.
- `main.py` calls `load_dotenv(override=True)`: `.env` wins over shell exports.
- All agent file output must go under `output/`.

## Rules

- Never commit `.env` and never print or copy secrets from it. Document new variables in `.env.example`.
- Don't commit anything in `output/`.
- Python 3.10 – 3.13. Manage dependencies with Poetry (`poetry add`), not pip.

## Docs

- `docs/ARCHITECTURE.md` describes the current state: update it with every architectural change.
- Record decisions as ADRs in `docs/adr/`; track planned work in `docs/TODO.md`.
- `examples/sample-app/` contains intentional flaws: never fix them in place.

## Gotchas

- CrewAI strips a leading `/` from `output_file`; keep output paths relative.
- The `pyproject.toml` description ("code generation") doesn't match the current Dockerfile-focused tasks.
