# 5. `examples/sample-app` as a shared test target

Date: 2026-10-27
Status: Accepted

## Context

Generating artifacts for an imaginary topic is hard to evaluate, and there's no real project ready to point the agents at.

## Decision

Add `examples/sample-app/`: a tiny Flask app with a Dockerfile and CI file containing **deliberate, documented flaws** (`examples/sample-app/KNOWN_ISSUES.md`). Both tracks are run against it, and results are checked against the known list.

## Consequences

- Agent quality becomes measurable (how many known issues were found).
- The sample app must never be "fixed" in place; fixes go in agent output.
- Using the tools on other projects comes later (`--project PATH`, `pipx install`).
