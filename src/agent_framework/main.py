import sys

from dotenv import load_dotenv

from agent_framework.engine import AgenticEngine


def get_topic(argv: list[str]) -> str:
    """Topic from CLI args, otherwise prompt interactively."""
    topic = " ".join(argv).strip()
    while not topic:
        topic = input("What would you like the agents to build? (e.g., 'A weather CLI tool'): ").strip()
    return topic


def main():
    # .env is the source of truth; don't let stale shell exports win.
    load_dotenv(override=True)
    topic = get_topic(sys.argv[1:])

    print("Starting Multi-Agent Dev Pipeline...")
    result = AgenticEngine().run_pipeline(topic)

    print("\n\n" + "=" * 50)
    print("FINAL GENERATED OUTPUT")
    print("=" * 50 + "\n")
    print(result)


if __name__ == "__main__":
    main()
