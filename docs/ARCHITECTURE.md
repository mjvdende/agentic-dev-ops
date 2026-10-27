# Architecture

Current state of the system. Keep this file up to date with every change; record decisions in [`adr/`](adr/). Planned work is in [`TODO.md`](TODO.md).

## Goal

Use a local LLM (LM Studio) to run multiple cooperating agents, via two tracks (ADR 0002):

1. **OpenCode + LM Studio subagents**: interactive, tool-using (below).
2. **CrewAI pipeline**: batch, no tools (below).

## Track 1: OpenCode + LM Studio

```
/audit [path]   (.opencode/command/audit.md, primary agent: build)
   ├─ task → architect    (read-only)  project summary
   ├─ task → security-qa  (read-only)  findings table
   ├─ task → developer    (edit only output/**)  hardened files
   └─ build writes output/opencode-audit/report.md
```

| File | Role |
|---|---|
| `opencode.json` | `lmstudio` provider (`@ai-sdk/openai-compatible`, `http://localhost:1234/v1`, key `{env:LLM_TOKEN}`), models, per-agent model = 26b |
| `.opencode/agent/*.md` | Subagent prompts and permissions |
| `.opencode/command/audit.md` | Orchestration prompt |

Benchmarks: `scripts/bench_opencode.sh`, scored by `score-audit` (`scoring.py`). Results in [`TEST_RESULTS.md`](TEST_RESULTS.md).

## Track 2: CrewAI pipelines

```
agents run <pipeline> [topic] [--project PATH] [--model M] [-v]
   │
main.py ── load_dotenv(override=True) ── LLMConfig (config.py)
   │        └─ project pipelines: read_project(PATH) → {project_files}  (project.py)
registry.py ── pipelines.yaml → Pipeline(steps)            (ADR 0006)
   │
engine.py  AgenticEngine.build_crew(pipeline)
   ├─ AgentFactory.create(step)   one shared crewai.LLM, no tools, max_iter=3
   ├─ TaskFactory.create(step)    output_file per step, context = earlier steps
   └─ Crew(sequential, task_callback=Progress) → output/<timestamp>-<pipeline>-<label>/
```

| Pipeline | Input | Steps → files |
|---|---|---|
| `generate` | topic | design → `design_doc.md`, dockerfile → `Dockerfile`, audit → `security_report.md` |
| `audit` | `--project PATH` | summary → `summary.md`, findings → `security_report.md`, dockerfile → hardened `Dockerfile` |

| Module | Responsibility |
|---|---|
| `main.py` | CLI (`agents list/run`, `run-agents` alias), progress, summary |
| `config.py` | `LLMConfig` from env (`LLM_TOKEN` > `LLM_API_KEY`), `max_tokens` (default 4096) |
| `registry.py` + `pipelines.yaml` | Pipeline definitions and validation |
| `project.py` | Inline a project's text files (line-numbered, size-capped, skips secrets/answer key) |
| `engine.py` | Builds and runs the crew per pipeline |
| `agents.py` / `tasks.py` | Generic factories: one agent + one task per step |
| `scoring.py` | `score-audit`: score a report against `KNOWN_ISSUES.md` |

About one LLM call per step. `audit` on the sample app: ~2.5 min, 13/14 (see [`TEST_RESULTS.md`](TEST_RESULTS.md)).

## Test target

`examples/sample-app/`: Flask app with deliberate flaws, listed in `KNOWN_ISSUES.md` (ADR 0005).

## Testing

`tests/` runs without an LLM (config, CLI parsing, crew wiring). Lint with ruff.
