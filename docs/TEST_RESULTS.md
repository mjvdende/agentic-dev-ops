# Test results

Benchmark log for both tracks against `examples/sample-app` (14 known issues, see `examples/sample-app/KNOWN_ISSUES.md`).

- **Score**: `poetry run score-audit <report.md>` (keyword heuristic, `src/agent_framework/scoring.py`); spot-checked by hand.
- **OpenCode runs**: `scripts/bench_opencode.sh [model ...]` → `output/bench/` (gitignored). All agents run on the same model.
- Hardware: local LM Studio on macOS, one model loaded at a time.

## Summary

| Track | Model | Prompt version | Time | Score | Recall | Fixed files written | Target modified |
|---|---|---|---:|---:|---:|---:|:---:|
| OpenCode `/audit` | gemma-4-26b-a4b | v1 (initial) | 317s | 11/14 | 79% | 0 | no |
| OpenCode `/audit` | gemma-4-26b-a4b | v2 (fixed prompts) | 323s | 11/14 | 79% | 4 | no |
| OpenCode `/audit` | gemma-4-e4b | v2 | 1451s | 4/14 | 29% | 2 | no |
| OpenCode `/audit` | qwen3-coder-30b | v2 | aborted | – | – | – | – |
| CrewAI `agents run audit` | gemma-4-26b-a4b | max_tokens 2048 | failed (step 3) | 13/14 | 93% | 0 (empty LLM answer) | no |
| CrewAI `agents run audit` | gemma-4-26b-a4b | max_tokens 4096 | 136s | 13/14 | 93% | 1 (Dockerfile) | no |
| CrewAI `run-agents` (topic) | gemma-4-e4b | output_file | 197s | n/a | – | 3 artifacts | – |
| CrewAI `run-agents` (topic) | gemma-4-26b-a4b | output_file | 188s | n/a | – | 3 artifacts | – |

CrewAI `generate` runs work from a topic and are not scored. CrewAI `audit` reports are scored from `security_report.md`.

## Per-issue detection (OpenCode `/audit`)

| # | Area | Issue | Severity | OC 26b v1 | OC 26b v2 | OC e4b v2 | CrewAI 26b |
|---:|---|---|---|:---:|:---:|:---:|:---:|
| 1 | Dockerfile | `python:latest` base | Medium | ✓ | ✓ | | ✓ |
| 2 | Dockerfile | Secret in `ENV` | High | ✓ | ✓ | ✓ | ✓ |
| 3 | Dockerfile | `ADD` / no `.dockerignore` | Medium | ✓ | ✓ | | ✓ |
| 4 | Dockerfile | Runs as root | High | ✓ | ✓ | | ✓ |
| 5 | Dockerfile | apt bloat | Low | ✓ | ✓ | ✓ | ✓ |
| 6 | Dockerfile | pip cache / unpinned deps | Medium | ✓ | ✓ | | ✓ |
| 7 | Dockerfile | Port 22 / CMD / no HEALTHCHECK | Medium | ✓ | ✓ | ✓ | ✓ |
| 8 | app.py | Command injection | Critical | | ✓ | ✓ | ✓ |
| 9 | app.py | `debug=True` | Critical | | ✓ | | ✓ |
| 10 | app.py | `changeme` default token | Medium | | | | ✓ |
| 11 | CI | Hardcoded registry password | High | ✓ | ✓ | |  |
| 12 | CI | `latest` tags | Medium | ✓ | | | ✓ |
| 13 | CI | `curl \| bash` | High | ✓ | ✓ | | ✓ |
| 14 | CI | No test/scan stage | Medium | ✓ | | | ✓ |
| | | **Critical found** | | 0/2 | 2/2 | 1/2 | 2/2 |
| | | **High found** | | 4/4 | 4/4 | 1/4 | 3/4 |

## Prompt versions

- **v1**: initial subagents. Developer tried to write into `examples/sample-app/`, was blocked by the `edit` permission and gave up. Security-qa never read `app.py`.
- **v2**: developer gets exact `output/opencode-audit/...` paths and "retry on rejection"; security-qa must glob all files (incl. hidden) and read source code, with a checklist; `/audit` names the task tool's required args.

## Observations

- v2 fixed both v1 failures: the critical app-code issues are found and files are written. Score stayed at 11/14 because CI coverage dropped (#12, #14), so run-to-run variance is roughly ±2 issues; one run per model is not conclusive.
- 26b's developer wrote an unrequested fixed `app.py` and skipped `.dockerignore`.
- e4b is **4.5× slower** than 26b in OpenCode, despite being the smaller model: it spends many turns on failed or repeated tool calls. Confirms ADR 0002: small models are poor at agentic tool use. For CrewAI (no tools) e4b and 26b take about the same time.
- The permission guard worked in every run: the target was never modified.
- Benchmarks take 5–25 min per model; the qwen3-coder-30b run was aborted for time.

- **CrewAI `audit` beat OpenCode** on the same 26b model: 13/14 in 136s vs 11/14 in ~320s. Inlining the files removes all tool calls, so the model can't skip a file and spends no turns navigating. Trade-off: no agentic exploration, so it only scales to small projects.
- At `max_tokens=2048` the 3rd step returned an empty answer (Gemma reasoning consumed the budget); 4096 fixed it.

## Open

- Run qwen3-coder-30b (`scripts/bench_opencode.sh qwen/qwen3-coder-30b`).
- Repeat runs (n≥3) per model to measure variance.
- Repeat CrewAI `audit` runs (n≥3) and try e4b there (no tools, so it may do much better than in OpenCode).
