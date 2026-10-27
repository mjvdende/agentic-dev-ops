import os

from crewai import Crew, Process

from .agents import AgentFactory
from .config import LLMConfig, load_llm_config
from .tasks import TaskFactory


class AgenticEngine:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or load_llm_config()
        # CrewAI internals (e.g. delegation tools) may build their own LLM from env.
        os.environ["OPENAI_API_BASE"] = self.config.base_url
        os.environ["OPENAI_API_KEY"] = self.config.api_key

    def build_crew(self) -> Crew:
        factory = AgentFactory(self.config)
        agents = {
            "architect": factory.get_architect(),
            "developer": factory.get_developer(),
            "qa": factory.get_qa(),
        }

        task_factory = TaskFactory(agents)
        design_task = task_factory.get_design_task()
        dev_task = task_factory.get_dev_task()
        qa_task = task_factory.get_qa_task()

        # Chain: design -> dev -> qa
        dev_task.context = [design_task]
        qa_task.context = [dev_task]

        return Crew(
            agents=list(agents.values()),
            tasks=[design_task, dev_task, qa_task],
            process=Process.sequential,
            verbose=True,
        )

    def run_pipeline(self, topic: str):
        return self.build_crew().kickoff(inputs={"topic": topic})
