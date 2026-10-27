import os
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from crewai import Crew, Process

from .agents import AgentFactory
from .config import LLMConfig, load_llm_config
from .registry import Pipeline
from .tasks import TaskFactory

OUTPUT_ROOT = Path("output")


def slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "run"


def make_run_dir(label: str, root: Path = OUTPUT_ROOT, now: datetime | None = None) -> Path:
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return root / f"{stamp}-{slugify(label)}"


class AgenticEngine:
    def __init__(self, config: LLMConfig | None = None, verbose: bool = False):
        self.config = config or load_llm_config()
        self.verbose = verbose
        # CrewAI internals may build their own LLM from env.
        os.environ["OPENAI_API_BASE"] = self.config.base_url
        os.environ["OPENAI_API_KEY"] = self.config.api_key

    def build_crew(self, pipeline: Pipeline, output_dir: Path, task_callback: Callable | None = None) -> Crew:
        agents_f = AgentFactory(self.config, verbose=self.verbose)
        tasks_f = TaskFactory(output_dir)
        agents, tasks = [], {}
        for step in pipeline.steps:
            agent = agents_f.create(step)
            agents.append(agent)
            tasks[step.name] = tasks_f.create(step, agent, [tasks[c] for c in step.context])
        return Crew(
            agents=agents,
            tasks=list(tasks.values()),
            process=Process.sequential,
            verbose=self.verbose,
            task_callback=task_callback,
        )

    def run(self, pipeline: Pipeline, inputs: dict, label: str, task_callback: Callable | None = None) -> Path:
        """Run a pipeline and return the folder containing its artifacts."""
        output_dir = make_run_dir(f"{pipeline.name}-{label}")
        output_dir.mkdir(parents=True, exist_ok=True)
        self.build_crew(pipeline, output_dir, task_callback).kickoff(inputs=inputs)
        return output_dir
