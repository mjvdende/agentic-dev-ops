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

## Track 2: CrewAI pipeline

```
run-agents [--verbose] "<topic>"
   │
main.py ── load_dotenv(override=True) ── LLMConfig (config.py)
   │
engine.py  AgenticEngine
   ├─ AgentFactory (agents.py)  one crewai.LLM shared by 3 agents, no tools
   ├─ TaskFactory  (tasks.py)   3 tasks, each with output_file
   └─ Crew(process=sequential, task_callback=progress)
        design ──context──▶ dockerfile ──context──▶ security audit
          │                    │                       │
   output/<run>/design_doc.md  Dockerfile        security_report.md
```

| Module | Responsibility |
|---|---|
| `main.py` | CLI parsing, progress lines, final summary |
| `config.py` | `LLMConfig` from env (`LLM_TOKEN` > `LLM_API_KEY`), LiteLLM model string, generation limits |
| `engine.py` | Builds agents/tasks/crew, creates the per-run output folder, runs it |
| `agents.py` | `AgentFactory`: Architect, DevOps Engineer, Security QA |
| `tasks.py` | `TaskFactory`: one task per artifact, results saved via `output_file` (ADR 0003) |

### Runtime characteristics

- About one LLM call per task (no tools, `max_iter` bounded). Run time is dominated by local model speed.
- Each run writes to `output/<YYYYmmdd-HHMMSS>-<slug>/`; nothing is overwritten.
- Connection: explicit `crewai.LLM(base_url, api_key)`; `OPENAI_API_BASE`/`OPENAI_API_KEY` are also exported for CrewAI internals.

## Test target

`examples/sample-app/`: Flask app with deliberate flaws, listed in `KNOWN_ISSUES.md` (ADR 0005).

## Testing

`tests/` runs without an LLM (config, CLI parsing, crew wiring). Lint with ruff.
