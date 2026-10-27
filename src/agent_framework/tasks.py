from pathlib import Path

from crewai import Task

# Each task's final answer is the artifact; CrewAI saves it via output_file (ADR 0003).
DESIGN_FILE = "design_doc.md"
DOCKERFILE = "Dockerfile"
REPORT_FILE = "security_report.md"


class TaskFactory:
    def __init__(self, agents: dict, output_dir: Path):
        self.agents = agents
        self.output_dir = output_dir

    def _out(self, name: str) -> str:
        return str(self.output_dir / name)

    def get_design_task(self) -> Task:
        return Task(
            description="Write a concise technical design document (max ~400 words) for: {topic}.",
            expected_output="The design document in Markdown. No preamble.",
            agent=self.agents["architect"],
            output_file=self._out(DESIGN_FILE),
        )

    def get_dev_task(self) -> Task:
        return Task(
            description="Write a production-grade, secure Dockerfile for {topic}, following the design.",
            expected_output="Only the Dockerfile contents. No Markdown fences, no explanation.",
            agent=self.agents["developer"],
            output_file=self._out(DOCKERFILE),
        )

    def get_qa_task(self) -> Task:
        return Task(
            description="Security-audit the Dockerfile for {topic}. List each issue with severity and a fix.",
            expected_output="A security report in Markdown. No preamble.",
            agent=self.agents["qa"],
            output_file=self._out(REPORT_FILE),
        )
