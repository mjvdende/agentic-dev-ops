import argparse
import time

from dotenv import load_dotenv

from agent_framework.config import load_llm_config
from agent_framework.engine import AgenticEngine

STEPS = 3


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="run-agents", description="Run the multi-agent Dockerfile pipeline.")
    parser.add_argument("topic", nargs="*", help="What to build, e.g. 'A Flask hello-world API'")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show full CrewAI agent logs")
    return parser.parse_args(argv)


def get_topic(words: list[str]) -> str:
    """Topic from CLI args, otherwise prompt interactively."""
    topic = " ".join(words).strip()
    while not topic:
        topic = input("What would you like the agents to build? (e.g., 'A weather CLI tool'): ").strip()
    return topic


class Progress:
    """Prints one line per finished task with its duration."""

    def __init__(self, total: int = STEPS):
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


def main(argv: list[str] | None = None):
    # .env is the source of truth; don't let stale shell exports win (ADR 0004).
    load_dotenv(override=True)
    args = parse_args(argv)
    topic = get_topic(args.topic)
    config = load_llm_config()

    print(f"Running {STEPS} agents on {config.model} for: {topic}", flush=True)
    progress = Progress()
    run_dir = AgenticEngine(config, verbose=args.verbose).run_pipeline(topic, task_callback=progress)

    print(f"\nDone in {progress.elapsed:.0f}s. Artifacts in {run_dir}/:")
    for f in sorted(run_dir.iterdir()):
        print(f"  - {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
