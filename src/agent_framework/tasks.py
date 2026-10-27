from pathlib import Path

from crewai import Agent, Task

from .registry import Step


class TaskFactory:
    """Builds one Task per pipeline step; CrewAI saves the answer via output_file (ADR 0003)."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def create(self, step: Step, agent: Agent, context: list[Task]) -> Task:
        return Task(
            description=step.task,
            expected_output=step.expected_output,
            agent=agent,
            context=context or None,
            output_file=str(self.output_dir / step.output),
        )
