import os
from .agents import AgentFactory
from .tasks import TaskFactory
from crewai import Crew, Process

class AgenticEngine:
    def __init__(self):
        # We MUST set these environment variables globally
        # so that CrewAI's internal factory uses LM Studio
        os.environ["OPENAI_API_BASE"] = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY", "lm-studio")

        self.llm_config = {
            "model": os.getenv("LLM_MODEL_NAME", "local-model"),
            "base_url": os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
            "api_key": os.getenv("LLM_API_KEY", "lm-studio")
        }

    def run_pipeline(self, topic: str):
        factory = AgentFactory(self.llm_config)
        agents = {
            'architect': factory.get_architect(),
            'developer': factory.get_developer(),
            'qa': factory.get_qa()
        }

        task_factory = TaskFactory(agents)

        # 1. Create the tasks individually first
        design_task = task_factory.get_design_task()
        dev_task = task_factory.get_dev_task()
        qa_task = task_factory.get_qa_task()

        # 2. NOW link them using the Task objects as context
        # This tells CrewAI: "To do DevTask, you need to look at DesignTask"
        dev_task.context = [design_task]
        qa_task.context = [dev_task]

        # 3. Assemble Crew with the correctly linked tasks
        crew = Crew(
            agents=list(agents.values()),
            tasks=[design_task, dev_task, qa_task],
            process=Process.sequential,
            verbose=True
        )

        return crew.kickoff(inputs={'topic': topic})

