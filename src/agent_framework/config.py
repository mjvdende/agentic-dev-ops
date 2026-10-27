import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_BASE_URL = "http://localhost:1234/v1"
DEFAULT_API_KEY = "lm-studio"
DEFAULT_MODEL = "local-model"


@dataclass(frozen=True)
class LLMConfig:
    model: str
    base_url: str
    api_key: str

    @property
    def litellm_model(self) -> str:
        """Model string in LiteLLM form (openai/<model>) for OpenAI-compatible servers."""
        return self.model if self.model.startswith("openai/") else f"openai/{self.model}"

    def __repr__(self) -> str:  # never leak the key in logs
        return f"LLMConfig(model={self.model!r}, base_url={self.base_url!r}, api_key='***')"


def load_llm_config(env: Mapping[str, str] | None = None) -> LLMConfig:
    """Build config from env. LLM_TOKEN takes precedence over LLM_API_KEY."""
    env = os.environ if env is None else env
    return LLMConfig(
        model=env.get("LLM_MODEL_NAME") or DEFAULT_MODEL,
        base_url=env.get("LLM_BASE_URL") or DEFAULT_BASE_URL,
        api_key=env.get("LLM_TOKEN") or env.get("LLM_API_KEY") or DEFAULT_API_KEY,
    )
