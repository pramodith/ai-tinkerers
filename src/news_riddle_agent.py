from crewai import Agent, Crew, LLM, Task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pydantic import BaseModel


class AINewsHeadlines(BaseModel):
    headlines: list[str]
    descriptions: list[str]
    dates: list[str]


class AINewsRiddle(BaseModel):
    riddles: list[str]
    answers: list[str]
    hints: list[str]


class AINewsRiddleAgent:
    """
    An agent that searches the web for the latest news, given a topic and creates riddles based on them.
    """

    def __init__(self, model_name: str = "gpt-4.1"):
        self.model_name = model_name
        self.web_search_tool = SerperDevTool()
        self.llm = LLM(model=self.model_name)

        self.news_search_agent = Agent(
            role="AI News Curator",
            goal=(
                "Generate a list of the 5 most relevant news updates that have occurred "
                "in the past 24 hours about {{topic}}. "
            ),
            backstory=(
                "You are a content creator that finds the most interesting and fun news updates."
            ),
            llm=self.llm,
            tools=[self.web_search_tool],
        )

        self.riddle_agent = Agent(
            role="Riddle Creator",
            goal=(
                "Create a riddles for each of the presented news headlines and descriptions. The answer to the riddle "
                "should be deduced from the headline and description clearly showing how it is based on the latest news."
                "Your response for should be a json object with three keys: 'riddles', 'answers', and 'hints'."
            ),
            backstory=("You are an expert at creating fun riddles."),
            llm=self.llm,
        )

        news_search_task = Task(
            description="Generate a list of the 5 most relevant news updates that have occurred in the past 24 hours about {topic},"
            "using the provided web search tool.",
            expected_output="A list of 5 news headlines, descriptions, and dates.",
            agent=self.news_search_agent,
            output_pydantic=AINewsHeadlines,
        )

        riddle_task = Task(
            description=(
                "Create a riddle based on the presented AI news."
                "The answer to the riddle should be deduced from the headline and description clearly showing how it is based on the latest news."
            ),
            expected_output="A riddle and its answer.",
            agent=self.riddle_agent,
            output_pydantic=AINewsRiddle,
        )

        self.crew: Crew = Crew(
            agents=[self.news_search_agent, self.riddle_agent],
            tasks=[news_search_task, riddle_task],
            verbose=False,
        )


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    # Create an instance of AINewsRiddleAgent
    agent = AINewsRiddleAgent()
    # Run the crew
    agent.llm.stream = False
    result = agent.crew.kickoff({"topic": "Arsenal F.C."})
    for part in result:
        print(part)
        print("\n\n")
