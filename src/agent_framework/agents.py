from crewai import LLM, Agent

from .config import LLMConfig

MAX_ITER = 3


class AgentFactory:
    def __init__(self, config: LLMConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.llm = LLM(
            model=config.litellm_model,
            base_url=config.base_url,
            api_key=config.api_key,
            max_tokens=config.max_tokens,
        )

    def _agent(self, role: str, goal: str, backstory: str) -> Agent:
        # No tools: the final answer is the artifact (ADR 0003).
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=self.llm,
            tools=[],
            max_iter=MAX_ITER,
            verbose=self.verbose,
            allow_delegation=False,
        )

    def get_architect(self) -> Agent:
        return self._agent("Software Architect", "Design {topic}", "Pragmatic system designer.")

    def get_developer(self) -> Agent:
        return self._agent("DevOps Engineer", "Containerize {topic}", "Writes minimal, secure Dockerfiles.")

    def get_qa(self) -> Agent:
        return self._agent("Security QA Engineer", "Audit the Dockerfile for {topic}", "Container security expert.")
