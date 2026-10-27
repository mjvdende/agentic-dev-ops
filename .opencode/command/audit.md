---
description: Multi-agent audit of a project (architect -> security-qa -> developer). Usage: /audit [path]
agent: build
model: lmstudio/google/gemma-4-26b-a4b
---

Run a multi-agent audit of the project at: $ARGUMENTS
If no path was given, use `examples/sample-app`.

Use the task tool to delegate (it requires `description`, `prompt` and `subagent_type`), strictly in this order, and wait for each result:

1. `architect` subagent: summarise the target project.
2. `security-qa` subagent: audit the target project. Pass it the architect's summary.
3. `developer` subagent: write hardened files into `output/opencode-audit/`. Pass it the security findings.

Finally, write `output/opencode-audit/report.md` containing the architect summary, the findings table and the developer's change list, and print a 5-line summary. Never modify files in the target project.
