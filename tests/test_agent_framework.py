from datetime import datetime
from pathlib import Path

import pytest

from agent_framework.config import (
    DEFAULT_API_KEY,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    load_llm_config,
)
from agent_framework.engine import AgenticEngine, make_run_dir, slugify
from agent_framework.main import Progress, build_parser, get_topic, resolve_inputs
from agent_framework.registry import load_pipelines

SAMPLE_APP = Path(__file__).parents[1] / "examples" / "sample-app"

# --- config ---


def test_defaults_when_env_empty():
    cfg = load_llm_config({})
    assert (cfg.model, cfg.base_url, cfg.api_key, cfg.max_tokens) == (
        DEFAULT_MODEL,
        DEFAULT_BASE_URL,
        DEFAULT_API_KEY,
        DEFAULT_MAX_TOKENS,
    )


def test_default_model_is_26b():
    assert DEFAULT_MODEL == "google/gemma-4-26b-a4b"


def test_llm_token_takes_precedence_over_api_key():
    assert load_llm_config({"LLM_TOKEN": "tok", "LLM_API_KEY": "key"}).api_key == "tok"


def test_api_key_used_when_no_token():
    assert load_llm_config({"LLM_API_KEY": "key"}).api_key == "key"


def test_max_tokens_from_env():
    assert load_llm_config({"LLM_MAX_TOKENS": "512"}).max_tokens == 512


def test_litellm_model_prefix():
    assert load_llm_config({"LLM_MODEL_NAME": "google/gemma"}).litellm_model == "openai/google/gemma"
    assert load_llm_config({"LLM_MODEL_NAME": "openai/x"}).litellm_model == "openai/x"


def test_repr_hides_key():
    assert "secret" not in repr(load_llm_config({"LLM_TOKEN": "secret"}))


# --- run folders ---


def test_slugify():
    assert slugify("A Flask hello-world API!") == "a-flask-hello-world-api"
    assert slugify("???") == "run"
    assert len(slugify("x" * 100)) == 40


def test_make_run_dir():
    d = make_run_dir("Flask API", root=Path("out"), now=datetime(2026, 10, 27, 9, 5, 1))
    assert d == Path("out/20261027-090501-flask-api")


# --- CLI ---


def test_topic_from_args():
    assert get_topic(["A", "weather", "CLI"]) == "A weather CLI"


def test_topic_prompts_until_non_empty(monkeypatch):
    answers = iter(["  ", "API server"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert get_topic([]) == "API server"


def test_parse_run_args():
    args = build_parser().parse_args(["run", "audit", "-p", "x", "-m", "m", "-v"])
    assert (args.pipeline, args.project, args.model, args.verbose) == ("audit", Path("x"), "m", True)
    assert build_parser().parse_args(["run", "generate", "a", "b"]).topic == ["a", "b"]


def test_resolve_inputs_project():
    pipeline = load_pipelines()["audit"]
    args = build_parser().parse_args(["run", "audit", "--project", str(SAMPLE_APP)])
    inputs, label = resolve_inputs(pipeline, args)
    assert label == "sample-app"
    assert "=== Dockerfile ===" in inputs["project_files"]


def test_resolve_inputs_project_requires_path():
    with pytest.raises(SystemExit):
        resolve_inputs(load_pipelines()["audit"], build_parser().parse_args(["run", "audit"]))


def test_progress_prints_steps(capsys):
    class Out:
        agent = "Software Architect"

    Progress(total=3)(Out())
    assert capsys.readouterr().out.startswith("[1/3] Software Architect done (")


# --- engine wiring (no LLM call) ---

RUN_DIR = Path("output/test-run")  # relative: CrewAI strips leading '/' from output_file


@pytest.mark.parametrize(
    ("name", "files"),
    [
        ("generate", ["design_doc.md", "Dockerfile", "security_report.md"]),
        ("audit", ["summary.md", "security_report.md", "Dockerfile"]),
    ],
)
def test_crew_wiring(name, files):
    cfg = load_llm_config({"LLM_MODEL_NAME": "m", "LLM_TOKEN": "t"})
    crew = AgenticEngine(cfg).build_crew(load_pipelines()[name], RUN_DIR)
    first, second, third = crew.tasks
    assert second.context == [first]
    assert third.context == [second]
    assert [Path(t.output_file).name for t in crew.tasks] == files
    assert all(Path(t.output_file).parent == RUN_DIR for t in crew.tasks)
    for agent in crew.agents:
        assert agent.llm.model == "openai/m"
        assert agent.tools == []
        assert agent.max_iter == 3
        assert agent.verbose is False
