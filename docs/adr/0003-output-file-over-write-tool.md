# 3. Save task results with `output_file` instead of a write tool

Date: 2026-10-27
Status: Accepted

## Context

Agents originally saved artifacts by calling a `write_file` tool. With small local models this was slow (each tool call is an extra LLM round trip) and unreliable: runs silently skipped `design_doc.md` or `security_report.md`, or wrote unrequested files (`app.py`, `requirements.txt`).

## Decision

Agents have no tools. Each task's final answer *is* the artifact, and CrewAI saves it via `Task(output_file=...)`. Agents get `max_iter` and the LLM gets `max_tokens` to bound run time.

## Consequences

- Every expected artifact is always written, one per task.
- Fewer LLM calls per run (about one per task).
- Agents can't produce multiple files per step; a step that needs that must be split or get a tool back deliberately.
- The `write_file` tool and its path-traversal guard are removed (paths are now set by code, not by the model).
