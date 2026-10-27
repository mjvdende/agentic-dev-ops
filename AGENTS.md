# AGENTS.md

Guidance for coding agents working in this repo.

## Project

CrewAI multi-agent PoC using a local LLM via LM Studio (OpenAI-compatible). A user-supplied topic flows through the Architect, Developer and QA agents in sequence, producing `output/design_doc.md`, `output/Dockerfile` and `output/security_report.md`.

## Commands

- Install: `poetry install`
- Run: `poetry run run-agents` (interactive prompt; requires LM Studio at `LLM_BASE_URL`)
- Tests and lint: none configured yet. If you add them, prefer `pytest` and `ruff`, and update this file.

## Layout

- `src/agent_framework/main.py`: entry point (`run-agents` script)
- `src/agent_framework/engine.py`: `AgenticEngine`, env setup, task chaining, `Crew` kickoff
- `src/agent_framework/agents.py`: `AgentFactory` (`get_architect`/`get_developer`/`get_qa`)
- `src/agent_framework/tasks.py`: `TaskFactory` (`get_design_task`/`get_dev_task`/`get_qa_task`)
- `src/agent_framework/tools.py`: `FileTools.write_file`
- `output/`: generated artifacts (gitignored)

## Conventions

- New agents go in `AgentFactory` and new tasks in `TaskFactory`. Wire task dependencies in `engine.py` via `task.context = [...]`.
- Task descriptions use `{topic}` placeholders, filled by `crew.kickoff(inputs=...)`.
- Tools use the `@tool` decorator from `crewai.tools`.
- Model strings use the LiteLLM form `openai/<model>`.
- LLM connection settings reach CrewAI through the `OPENAI_API_BASE` and `OPENAI_API_KEY` env vars, which `engine.py` sets. `llm_config["base_url"]` and `llm_config["api_key"]` are currently unused.
- All agent file output must go under `output/`.

## Rules

- Never commit `.env` and never print or copy secrets from it. Document new variables in `.env.example`.
- Don't commit anything in `output/`.
- Python 3.10 – 3.13. Manage dependencies with Poetry (`poetry add`), not pip.

## Gotchas

- `write_file` doesn't guard against `../` paths.
- The `pyproject.toml` description ("code generation") doesn't match the current Dockerfile-focused tasks.
