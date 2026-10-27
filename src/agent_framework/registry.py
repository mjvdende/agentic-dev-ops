"""Pipeline registry: loads pipeline definitions from pipelines.yaml (ADR 0006)."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_REGISTRY = Path(__file__).with_name("pipelines.yaml")
INPUT_KINDS = ("topic", "project")


@dataclass(frozen=True)
class Step:
    name: str
    role: str
    goal: str
    backstory: str
    task: str
    expected_output: str
    output: str
    context: tuple[str, ...] = ()


@dataclass(frozen=True)
class Pipeline:
    name: str
    description: str
    input: str
    steps: tuple[Step, ...] = field(default_factory=tuple)


class RegistryError(ValueError):
    pass


def parse_pipelines(data: dict) -> dict[str, Pipeline]:
    pipelines = {}
    for name, spec in (data or {}).items():
        if spec.get("input") not in INPUT_KINDS:
            raise RegistryError(f"{name}: input must be one of {INPUT_KINDS}")
        steps, seen = [], set()
        for raw in spec.get("steps") or []:
            step = Step(**{**raw, "context": tuple(raw.get("context") or ())})
            if missing := set(step.context) - seen:
                raise RegistryError(f"{name}.{step.name}: context refers to unknown/later step(s) {sorted(missing)}")
            if step.name in seen:
                raise RegistryError(f"{name}: duplicate step {step.name}")
            seen.add(step.name)
            steps.append(step)
        if not steps:
            raise RegistryError(f"{name}: no steps")
        pipelines[name] = Pipeline(name, spec.get("description", ""), spec["input"], tuple(steps))
    return pipelines


def load_pipelines(path: Path = DEFAULT_REGISTRY) -> dict[str, Pipeline]:
    return parse_pipelines(yaml.safe_load(path.read_text()))
