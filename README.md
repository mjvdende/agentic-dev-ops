# agentic-dev-ops

A proof-of-concept multi-agent pipeline built on [CrewAI](https://www.crewai.com/) and backed by a local LLM served by [LM Studio](https://lmstudio.ai/) (or any OpenAI-compatible endpoint).

Given a topic, three agents run in sequence:

1. **Architect**: writes a design document → `output/design_doc.md`
2. **Developer**: writes a Dockerfile based on the design → `output/Dockerfile`
3. **QA**: reviews the Dockerfile for security issues → `output/security_report.md`

## Requirements

- Python 3.10 – 3.13
- [Poetry](https://python-poetry.org/)
- LM Studio (or another OpenAI-compatible server) running with a model loaded

## Setup

```bash
poetry install
cp .env.example .env   # then edit values
```

`.env` variables:

| Variable         | Default                    | Description                         |
|------------------|----------------------------|-------------------------------------|
| `LLM_BASE_URL`   | `http://localhost:1234/v1` | OpenAI-compatible API base URL      |
| `LLM_TOKEN`      | —                          | API token; takes precedence over `LLM_API_KEY` |
| `LLM_API_KEY`    | `lm-studio`                | Fallback API key                    |
| `LLM_MODEL_NAME` | `google/gemma-4-26b-a4b`            | Model identifier loaded in LM Studio |

## Usage

```bash
poetry run run-agents
```

Pass the topic as an argument (add `-v` for full agent logs) (`poetry run run-agents "A Flask hello-world API"`) or enter it when prompted. Values in `.env` override variables already exported in your shell. Each run prints one progress line per agent and writes to its own folder, `output/<timestamp>-<topic>/`.

## How it works

```
src/agent_framework/
  main.py    Entry point: loads .env, prompts for a topic, runs the engine
  engine.py  AgenticEngine: configures LLM env vars, builds agents/tasks, runs a sequential Crew
  agents.py  AgentFactory: Architect, Developer and QA agents
  tasks.py   TaskFactory: design, dev and QA tasks (templated with {topic})
  config.py  LLMConfig + load_llm_config (env -> config)
```

Tasks are chained via context: design → dev → qa. LLM connection settings reach CrewAI/LiteLLM through the `OPENAI_API_BASE` and `OPENAI_API_KEY` environment variables set in `engine.py`.

## Development

```bash
poetry run pytest
poetry run ruff check src tests
```

## Known limitations

- Runs take ~3 min on `gemma-4-26b-a4b` locally.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/adr/`](docs/adr/) and [`docs/TODO.md`](docs/TODO.md). `examples/sample-app/` is a deliberately flawed test target.

