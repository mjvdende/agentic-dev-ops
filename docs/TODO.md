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
- [ ] Smoke test marked `@pytest.mark.llm` (skipped by default) checking the audit finds known flaws

## Track 1: OpenCode + LM Studio

- [ ] Project-level `opencode.json` with an `lmstudio` provider (`@ai-sdk/openai-compatible`, `http://localhost:1234/v1`, 26b default, e4b optional)
- [ ] Subagents in `.opencode/agent/`: `architect`, `developer`, `security-qa` (reviewers read-only)
- [ ] `/audit` command running the subagents on `examples/sample-app`
- [ ] README how-to + e4b vs 26b comparison notes

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
