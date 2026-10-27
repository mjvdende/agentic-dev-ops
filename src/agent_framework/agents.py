from crewai import Agent
from .tools import FileTools  # Import our new tool

class AgentFactory:
    def __init__(self, llm_config: dict):
        # 1. FIRST: Assign the config to the instance
        self.llm_config = llm_config

        # 2. SECOND: Now that self.llm_config exists, we can use it
        # We use a fallback if 'model' is missing to prevent further crashes
        model_name = self.llm_config.get('model', 'local-model')
        self.llm_string = f"openai/{model_name}"

    def get_architect(self) -> Agent:
        return Agent(
            role='Software Architect',
            goal='Design a technical specification for {topic}',
            backstory="Expert in system design.",
            llm=self.llm_string,
            tools=[FileTools.write_file], # <--- ADDED TOOL
            verbose=True,
            allow_delegation=False
        )

    def get_developer(self) -> Agent:
        return Agent(
            role='Senior Python Developer',
            goal='Implement the code for {topic}',
            backstory="Expert in writing clean Python code.",
            llm=self.llm_string,
            tools=[FileTools.write_file], # <--- ADDED TOOL
            verbose=True,
            allow_delegation=False
        )

    def get_qa(self) -> Agent:
        return Agent(
            role='QA Automation Engineer',
            goal='Generate a Pytest suite for {topic}',
            backstory="Expert in testing.",
            llm=self.llm_string,
            tools=[FileTools.write_file], # <--- ADDED TOOL
            verbose=True,
            allow_delegation=True
        )

