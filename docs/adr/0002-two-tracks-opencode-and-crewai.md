# 2. Two tracks: OpenCode subagents and a CrewAI pipeline

Date: 2026-10-27
Status: Accepted

## Context

The original goal: "show me how I can use LM Studio with OpenCode and let's create a project using multiple agents". There are two different ways to get multiple agents working against a local LLM:

- **Interactive**: a coding agent (OpenCode) delegates to specialised subagents, using tools on a real project.
- **Batch**: a framework (CrewAI) runs a fixed chain of agents, reproducible and scriptable.

Alternatives considered: replacing CrewAI with a plain prompt chain (fastest, but defeats the purpose of learning a multi-agent framework).

## Decision

Keep both tracks in this repo and compare them on the same target (`examples/sample-app`, ADR 0005):

1. **OpenCode + LM Studio**: project-level `opencode.json` and `.opencode/agent/*.md` subagents.
2. **CrewAI pipeline**: slimmed down (ADR 0003) and later grown into a pipeline registry with a CLI.

Default model is `google/gemma-4-26b-a4b`, since smaller models (e.g. `gemma-4-e4b`) are unreliable at tool calling. e4b remains usable for CrewAI steps that need no tools.

## Consequences

- Two configurations to maintain, but each answers a different half of the goal.
- Track 1 depends on the local model's tool-calling quality; results will be measured, not assumed.
