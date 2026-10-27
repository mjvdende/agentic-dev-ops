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
poetry run agents list                                        # available pipelines
poetry run agents run audit --project examples/sample-app     # audit an existing project
poetry run agents run generate "A Flask hello-world API"      # design + Dockerfile + audit from a topic
poetry run agents run audit -p ../other-repo -m google/gemma-4-e4b -v   # other model, full logs
poetry run score-audit output/<run>/security_report.md        # score against the sample app's known issues
```

`run-agents "<topic>"` still works as a shortcut for `agents run generate`. Each run prints one progress line per agent and writes to `output/<timestamp>-<pipeline>-<label>/`. Values in `.env` override variables already exported in your shell.

New pipelines are added in `src/agent_framework/pipelines.yaml` (no code needed).

To use the CLI in other repos: `pipx install /path/to/agentic-dev-ops` (untested), then run `agents ...` there. It needs the `LLM_*` variables in that repo's `.env` or your shell, and writes to `./output/`.

## OpenCode + LM Studio (multi-agent audit)

This repo ships a project-level [OpenCode](https://opencode.ai) setup that uses LM Studio as provider:

- `opencode.json`: `lmstudio` provider at `http://localhost:1234/v1`, API key from `LLM_TOKEN`
- `.opencode/agent/`: subagents `architect`, `security-qa` (read-only) and `developer` (may only write to `output/`)
- `.opencode/command/audit.md`: `/audit [path]` runs architect → security-qa → developer

`LLM_TOKEN` must be in your shell environment (e.g. `set -a; source .env; set +a`), then:

```bash
opencode                                   # then type: /audit examples/sample-app
opencode run --command audit examples/sample-app   # headless
```

Results: `output/opencode-audit/report.md`. Compare with `examples/sample-app/KNOWN_ISSUES.md`. Restart OpenCode after changing any of these files.

## How it works

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Benchmarks: [`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md).

## Development

```bash
poetry run pytest
poetry run ruff check src tests
```

## Known limitations

- Runs take 2–5 min on `gemma-4-26b-a4b` locally.
- `audit` inlines all project files (~60 KB cap), so it suits small projects.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/adr/`](docs/adr/) and [`docs/TODO.md`](docs/TODO.md). `examples/sample-app/` is a deliberately flawed test target.

