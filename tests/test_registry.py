import pytest

from agent_framework.project import read_project
from agent_framework.registry import RegistryError, load_pipelines, parse_pipelines

STEP = {"role": "r", "goal": "g", "backstory": "b", "task": "t", "expected_output": "e"}


def test_builtin_pipelines_load():
    pipelines = load_pipelines()
    assert {"generate", "audit"} <= set(pipelines)
    assert pipelines["generate"].input == "topic"
    assert pipelines["audit"].input == "project"


def test_context_must_refer_to_earlier_step():
    data = {"p": {"input": "topic", "steps": [{**STEP, "name": "a", "output": "a.md", "context": ["b"]}]}}
    with pytest.raises(RegistryError, match="unknown/later"):
        parse_pipelines(data)


def test_invalid_input_kind():
    with pytest.raises(RegistryError, match="input"):
        parse_pipelines({"p": {"input": "url", "steps": [{**STEP, "name": "a", "output": "a"}]}})


def test_empty_steps_rejected():
    with pytest.raises(RegistryError, match="no steps"):
        parse_pipelines({"p": {"input": "topic", "steps": []}})


def test_read_project_skips_answer_key_and_noise(tmp_path):
    (tmp_path / "app.py").write_text("print('hi')\n")
    (tmp_path / "KNOWN_ISSUES.md").write_text("answers")
    (tmp_path / ".env").write_text("SECRET=1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x")
    (tmp_path / "img.bin").write_bytes(b"\xff\xfe\x00")
    out = read_project(tmp_path)
    assert "=== app.py ===" in out and "   1 print('hi')" in out
    assert "answers" not in out and "SECRET" not in out and ".git" not in out and "img.bin" not in out


def test_read_project_size_limit(tmp_path):
    for i in range(5):
        (tmp_path / f"f{i}.txt").write_text("x" * 1000)
    assert "omitted" in read_project(tmp_path, max_total=2500)


def test_read_project_missing_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_project(tmp_path / "nope")
