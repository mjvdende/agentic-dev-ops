import pytest

from agent_framework.config import DEFAULT_API_KEY, DEFAULT_BASE_URL, DEFAULT_MODEL, load_llm_config
from agent_framework.engine import AgenticEngine
from agent_framework.main import get_topic
from agent_framework.tools import safe_write

# --- config ---

def test_defaults_when_env_empty():
    cfg = load_llm_config({})
    assert (cfg.model, cfg.base_url, cfg.api_key) == (DEFAULT_MODEL, DEFAULT_BASE_URL, DEFAULT_API_KEY)


def test_llm_token_takes_precedence_over_api_key():
    cfg = load_llm_config({"LLM_TOKEN": "tok", "LLM_API_KEY": "key"})
    assert cfg.api_key == "tok"


def test_api_key_used_when_no_token():
    assert load_llm_config({"LLM_API_KEY": "key"}).api_key == "key"


def test_litellm_model_prefix():
    assert load_llm_config({"LLM_MODEL_NAME": "google/gemma"}).litellm_model == "openai/google/gemma"
    assert load_llm_config({"LLM_MODEL_NAME": "openai/x"}).litellm_model == "openai/x"


def test_repr_hides_key():
    assert "secret" not in repr(load_llm_config({"LLM_TOKEN": "secret"}))


# --- safe_write ---

def test_writes_inside_base(tmp_path):
    msg = safe_write("Dockerfile", "FROM python", base_dir=tmp_path)
    assert "Successfully" in msg
    assert (tmp_path / "Dockerfile").read_text() == "FROM python"


def test_creates_subdirectories(tmp_path):
    safe_write("a/b/c.md", "x", base_dir=tmp_path)
    assert (tmp_path / "a/b/c.md").exists()


@pytest.mark.parametrize("name", ["../evil.txt", "a/../../evil.txt", "/etc/evil.txt", "."])
def test_refuses_escaping_paths(tmp_path, name):
    base = tmp_path / "out"
    msg = safe_write(name, "x", base_dir=base)
    assert msg.startswith("Refused")
    assert not (tmp_path / "evil.txt").exists()


# --- main ---

def test_topic_from_args():
    assert get_topic(["A", "weather", "CLI"]) == "A weather CLI"


def test_topic_prompts_until_non_empty(monkeypatch):
    answers = iter(["  ", "API server"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert get_topic([]) == "API server"


# --- engine wiring (no LLM call) ---

def test_crew_wiring():
    cfg = load_llm_config({"LLM_MODEL_NAME": "m", "LLM_TOKEN": "t"})
    crew = AgenticEngine(cfg).build_crew()
    design, dev, qa = crew.tasks
    assert len(crew.agents) == 3
    assert dev.context == [design]
    assert qa.context == [dev]
    assert all(a.llm.model == "openai/m" for a in crew.agents)
    assert design.output_file == "output/design_doc.md"
