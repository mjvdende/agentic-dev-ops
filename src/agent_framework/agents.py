from crewai import LLM, Agent

from .config import LLMConfig
from .tools import FileTools


class AgentFactory:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = LLM(
            model=config.litellm_model,
            base_url=config.base_url,
            api_key=config.api_key,
        )

    def _agent(self, role: str, goal: str, backstory: str, allow_delegation: bool = False) -> Agent:
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            tools=[FileTools.write_file],
            verbose=True,
            allow_delegation=allow_delegation,
        )

    def get_architect(self) -> Agent:
        return self._agent(
            "Software Architect",
            "Design a technical specification for {topic}",
            "Expert in system design.",
        )

    def get_developer(self) -> Agent:
        return self._agent(
            "DevOps Engineer",
            "Write a production-grade Dockerfile for {topic}",
            "Expert in containerization and secure Docker images.",
        )

    def get_qa(self) -> Agent:
        return self._agent(
            "Security QA Engineer",
            "Audit the Dockerfile for {topic} for security issues",
            "Expert in container security and best practices.",
        )
