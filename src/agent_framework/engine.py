import os
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from crewai import Crew, Process

from .agents import AgentFactory
from .config import LLMConfig, load_llm_config
from .tasks import TaskFactory

OUTPUT_ROOT = Path("output")


def slugify(text: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_len].rstrip("-") or "run"


def make_run_dir(topic: str, root: Path = OUTPUT_ROOT, now: datetime | None = None) -> Path:
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return root / f"{stamp}-{slugify(topic)}"


class AgenticEngine:
    def __init__(self, config: LLMConfig | None = None, verbose: bool = False):
        self.config = config or load_llm_config()
        self.verbose = verbose
        # CrewAI internals may build their own LLM from env.
        os.environ["OPENAI_API_BASE"] = self.config.base_url
        os.environ["OPENAI_API_KEY"] = self.config.api_key

    def build_crew(self, output_dir: Path, task_callback: Callable | None = None) -> Crew:
        factory = AgentFactory(self.config, verbose=self.verbose)
        agents = {
            "architect": factory.get_architect(),
            "developer": factory.get_developer(),
            "qa": factory.get_qa(),
        }

        tasks = TaskFactory(agents, output_dir)
        design_task = tasks.get_design_task()
        dev_task = tasks.get_dev_task()
        qa_task = tasks.get_qa_task()

        # Chain: design -> dev -> qa
        dev_task.context = [design_task]
        qa_task.context = [dev_task]

        return Crew(
            agents=list(agents.values()),
            tasks=[design_task, dev_task, qa_task],
            process=Process.sequential,
            verbose=self.verbose,
            task_callback=task_callback,
        )

    def run_pipeline(self, topic: str, task_callback: Callable | None = None) -> Path:
        """Run the pipeline and return the folder containing the artifacts."""
        output_dir = make_run_dir(topic)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.build_crew(output_dir, task_callback).kickoff(inputs={"topic": topic})
        return output_dir
