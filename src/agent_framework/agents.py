from crewai import LLM, Agent

from .config import LLMConfig
from .registry import Step

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

    def create(self, step: Step) -> Agent:
        # No tools: the final answer is the artifact (ADR 0003).
        return Agent(
            role=step.role,
            goal=step.goal,
            backstory=step.backstory,
            llm=self.llm,
            tools=[],
            max_iter=MAX_ITER,
            verbose=self.verbose,
            allow_delegation=False,
        )
