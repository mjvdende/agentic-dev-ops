import argparse
import time
from dataclasses import replace
from pathlib import Path

from dotenv import load_dotenv

from agent_framework.config import load_llm_config
from agent_framework.engine import AgenticEngine
from agent_framework.project import read_project
from agent_framework.registry import Pipeline, load_pipelines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agents", description="Run multi-agent pipelines on a local LLM.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available pipelines")
    run = sub.add_parser("run", help="Run a pipeline")
    run.add_argument("pipeline", help="Pipeline name (see `agents list`)")
    run.add_argument("topic", nargs="*", help="Topic, for topic pipelines (e.g. generate)")
    run.add_argument("-p", "--project", type=Path, help="Project directory, for project pipelines (e.g. audit)")
    run.add_argument("-m", "--model", help="Override LLM_MODEL_NAME for this run")
    run.add_argument("-v", "--verbose", action="store_true", help="Show full CrewAI agent logs")
    return parser


def get_topic(words: list[str]) -> str:
    """Topic from CLI args, otherwise prompt interactively."""
    topic = " ".join(words).strip()
    while not topic:
        topic = input("What would you like the agents to build? (e.g., 'A weather CLI tool'): ").strip()
    return topic


def resolve_inputs(pipeline: Pipeline, args: argparse.Namespace) -> tuple[dict, str]:
    """Return (crew inputs, label for the run folder)."""
    if pipeline.input == "project":
        if not args.project:
            raise SystemExit(f"Pipeline '{pipeline.name}' needs --project PATH")
        project = args.project.resolve()
        return {"project_name": project.name, "project_files": read_project(project)}, project.name
    topic = get_topic(args.topic)
    return {"topic": topic}, topic


class Progress:
    """Prints one line per finished task with its duration."""

    def __init__(self, total: int):
        self.total = total
        self.done = 0
        self.start = self.last = time.monotonic()

    def __call__(self, output) -> None:
        self.done += 1
        now = time.monotonic()
        agent = getattr(output, "agent", "agent")
        print(f"[{self.done}/{self.total}] {agent} done ({now - self.last:.0f}s)", flush=True)
        self.last = now

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.start


def cmd_list(pipelines: dict[str, Pipeline]) -> None:
    for p in pipelines.values():
        arg = "--project PATH" if p.input == "project" else '"<topic>"'
        print(f"{p.name:<10} {p.description}\n{'':<10} agents run {p.name} {arg}  ({len(p.steps)} steps)")


def cmd_run(pipelines: dict[str, Pipeline], args: argparse.Namespace) -> None:
    if args.pipeline not in pipelines:
        raise SystemExit(f"Unknown pipeline '{args.pipeline}'. Available: {', '.join(pipelines)}")
    pipeline = pipelines[args.pipeline]
    inputs, label = resolve_inputs(pipeline, args)
    config = load_llm_config()
    if args.model:
        config = replace(config, model=args.model)

    print(f"Running '{pipeline.name}' ({len(pipeline.steps)} agents) on {config.model} for: {label}", flush=True)
    progress = Progress(len(pipeline.steps))
    run_dir = AgenticEngine(config, verbose=args.verbose).run(pipeline, inputs, label, task_callback=progress)

    print(f"\nDone in {progress.elapsed:.0f}s. Artifacts in {run_dir}/:")
    for f in sorted(run_dir.iterdir()):
        print(f"  - {f.name} ({f.stat().st_size} bytes)")


def main(argv: list[str] | None = None) -> None:
    # .env is the source of truth; don't let stale shell exports win (ADR 0004).
    load_dotenv(override=True)
    args = build_parser().parse_args(argv)
    pipelines = load_pipelines()
    if args.command == "list":
        cmd_list(pipelines)
    else:
        cmd_run(pipelines, args)


def legacy_main() -> None:
    """`run-agents [topic]`: kept as a shortcut for `agents run generate [topic]`."""
    import sys

    main(["run", "generate", *sys.argv[1:]])


if __name__ == "__main__":
    main()
