import os
import json
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
load_dotenv()


@CrewBase
class GetInfoBusiness():
	"""GetInfoBusiness crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	output_file = None

	os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')

	serper_tool = SerperDevTool()


	def set_output_file(self, filename):
		self.output_file = filename

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[self.serper_tool]
		)

	@agent
	def copywriter(self) -> Agent:
		return Agent(
			config=self.agents_config['copywriter'],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)


	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			tools=[self.serper_tool]
		)

	@task
	def email_task(self) -> Task:
		return Task(
			config=self.tasks_config['email_task']
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			context=[self.research_task(), self.email_task()]
		)


	@crew
	def crew(self) -> Crew:
		"""Creates the GetInfoBusiness crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
