import os
from dotenv import load_dotenv
from agent_framework.engine import AgenticEngine

def main():
    load_dotenv() # Loads LLM credentials

    print("🚀 Starting Multi-Agent Dev Pipeline...")
    topic = input("What would you like the agents to build? (e.g., 'A weather CLI tool'): ")

    engine = AgenticEngine()
    result = engine.run_pipeline(topic)

    print("\n\n" + "="*50)
    print("FINAL GENERATED OUTPUT")
    print("="*50 + "\n")
    print(result)

if __name__ == "__main__":
    main()
