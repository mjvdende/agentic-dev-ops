from crewai import Task

class TaskFactory:
    def __init__(self, agents):
        self.agents = agents

    def get_design_task(self) -> Task:
        return Task(
            description="""Create a technical design document for {topic}. 
            CRITICAL: You MUST use the 'write_file' tool to save this design as 'design_doc.md'. 
            Do not just print it; you must call the tool.""",
            expected_output="A saved design document in output/design_doc.md",
            agent=self.agents['architect']
        )

    def get_dev_task(self) -> Task:
        return Task(
            description="""Implement the production-grade Dockerfile for {topic} based on the architect's design.
            CRITICAL: You MUST use the 'write_file' tool to save the actual code/Dockerfile as 'Dockerfile'. 
            Do not just output text in the chat; the file MUST be written via the tool.""",
            expected_output="A saved Dockerfile in output/Dockerfile",
            agent=self.agents['developer']
        )

    def get_qa_task(self) -> Task:
        return Task(
            description="""Review the 'Dockerfile' created by the developer. 
            Perform a security audit and create a report.
            CRITICAL: You MUST use the 'write_file' tool to save your findings as 'security_report.md'.""",
            expected_output="A saved security report in output/security_report.md",
            agent=self.agents['qa']
        )
    