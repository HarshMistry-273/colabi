from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain_community.tools import TavilySearchResults
from src.config import Config
from langchain_openai import ChatOpenAI


class CrewAgent:
    def __init__(
        self,
        role,
        goal,
        backstory,
        expected_output,
        model: str = Config.MODEL_NAME,
    ):
        self.model = ChatOpenAI(
            model=model,
            api_key=Config.OPENAI_API_KEY,
        )
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.search = TavilySearchResults(
            max_results=10,
            search_depth="advanced",
            include_answer=True,
            # include_raw_content=True,
        )
        self.expected_output = expected_output
        self.create_tool()
        self.create_agent()
        self.initialize_task()
        self.create_crew()
        # self.google_search_wrapper = GoogleSearchAPIWrapper(
        #     google_api_key=Config.GOOGLE_API_KEY, google_cse_id=Config.GOOGLE_CSE_ID
        # )

    def create_tool(self) -> None:
        self.serper_tool = Tool(
            name="google_search",
            # func=self.search.run,
            func=lambda query: self.search.invoke(query),
            description="Search Google for recent results.",
        )

    def create_agent(self) -> None:

        self.research_agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.model,
            tools=[self.serper_tool],
            verbose=True,
        )

    def initialize_task(self):
        prompt = """Conduct an in-depth web search on {description}, focusing on gathering the most recent and credible data available. Provide a detailed yet concise summary, emphasizing key points, trends, and any notable developments. Ensure that all information is gathered from authoritative, trustworthy sources. Include a valid and working link to each data source in the following format: [http://example.com/dataset], and verify that all insights are precise, relevant, and from reputable publications or datasets."""
        self.research_task = Task(
            description=prompt,
            expected_output=self.expected_output,
            # expected_output="Summarize key insights and relevant data from the search results in 3-4 sentences. If multiple articles are referenced, provide a brief summary of each.",
            agent=self.research_agent,
        )

        # self.write_task = Task(
        #     description="Write a summary on the {topic}",
        #     expected_output="A summary of key in  sights and relevant data from of {topic}.",
        #     agent=self.writer_agent,
        #     output_file="one.md",
        # )

    def create_crew(self):
        self.crew = Crew(
            agents=[self.research_agent],  # , self.writer_agent],
            tasks=[self.research_task],  # , self.write_task],
            # process=Process.sequential,
            verbose=True,
            # memory=True,
        )

    def main(self, description: str):
        response = self.crew.kickoff(inputs={"description": description})
        return response
