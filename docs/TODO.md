# TODO

Suggested improvements and quick fixes. Check items off as they land and update `ARCHITECTURE.md`.

## Quick fixes (CrewAI pipeline)

- [x] Save every task result via `output_file`; drop the `write_file` tool (ADR 0003)
- [x] Bound runs with `max_iter` and `max_tokens`; shorten prompts
- [x] `--verbose` flag; default is one progress line per step with timing
- [x] Per-run output folder `output/<timestamp>-<slug>/`
- [x] Final summary with generated files and total time
- [x] Default model `google/gemma-4-26b-a4b`

## Test project

- [x] `examples/sample-app` with documented deliberate flaws (ADR 0005)
- [x] `score-audit` scorer against KNOWN_ISSUES
- [ ] Smoke test marked `@pytest.mark.llm` (skipped by default) checking the audit finds known flaws

## Track 1: OpenCode + LM Studio

- [x] Project-level `opencode.json` with an `lmstudio` provider (`@ai-sdk/openai-compatible`, `http://localhost:1234/v1`, 26b default, e4b optional)
- [x] Subagents in `.opencode/agent/`: `architect`, `developer`, `security-qa` (reviewers read-only)
- [x] `/audit` command running the subagents on `examples/sample-app`
- [x] README how-to
- [x] e4b vs 26b comparison on `/audit` (docs/TEST_RESULTS.md)
- [ ] Benchmark `qwen/qwen3-coder-30b` and repeat runs (n≥3)
- [x] Fix: developer subagent reports changes but writes no files (check `edit` permission pattern / force write)
- [x] Fix: security-qa skipped `app.py` (missed known issues #8–#10); make it list and read all source files first

## Track 2: CrewAI growth

- [ ] Pipeline registry (YAML): `generate` (current) and `audit <path>` (real files)
- [ ] CLI: `agents run <pipeline> [--project PATH] [--model] [--verbose]`
- [ ] `pipx install .` so it works from other repos
- [ ] Unit tests for registry and CLI

## Later

- [ ] PR/MR review pipeline
- [ ] CI pipeline generator
- [ ] Incident postmortem pipeline
- [ ] Fix `pyproject.toml` description and authors placeholder
