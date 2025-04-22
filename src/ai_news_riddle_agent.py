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
    An agent that searches the web for the latest AI news, given a topic and creates riddles based on them.
    """

    def __init__(self, model_name: str = "gpt-4.1-nano"):
        self.model_name = model_name
        self.web_search_tool = SerperDevTool()
        self.llm = LLM(model=self.model_name)

        self.ai_news_search_agent = Agent(
            role="AI News Curator",
            goal=(
                "Generate a list of the 5 most relevant AI updates that have occurred "
                "in the past 24 hours about {{topic}}. "
            ),
            backstory=(
                "You are an experienced AI content creator, with a deep understanding of AI "
                "and its applications. You have a keen eye for the latest developments in "
                "the field and are always looking for new and innovative ways to present "
                "AI news and updates."
            ),
            llm=self.llm,
            tools=[self.web_search_tool],
        )

        self.riddle_agent = Agent(
            role="Riddle Creator",
            goal=(
                "Create a riddles for each of the presented AI news headlines. The answer to the riddle "
                "should be the main subject that the news deals with."
                "Your response for should be a json object with three keys: 'riddles', 'answers', and 'hints'."
            ),
            backstory=("You are an expert at creating fun riddles."),
            llm=self.llm,
        )

        ai_news_search_task = Task(
            description="Generate a list of the 5 most relevant AI updates that have occurred in the past 24 hours about {topic},"
            "using the provided web search tool.",
            expected_output="A list of 5 AI news headlines.",
            agent=self.ai_news_search_agent,
            output_pydantic=AINewsHeadlines,
        )

        riddle_task = Task(
            description=(
                "Create a riddle based on the presented AI news."
                "The answer to the riddle should be the main subject that the news deals with."
            ),
            expected_output="A riddle and its answer.",
            agent=self.riddle_agent,
            output_pydantic=AINewsRiddle,
        )

        self.crew: Crew = Crew(
            agents=[self.ai_news_search_agent, self.riddle_agent],
            tasks=[ai_news_search_task, riddle_task],
            verbose=False,
        )


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    # Create an instance of AINewsRiddleAgent
    agent = AINewsRiddleAgent()
    # Run the crew
    agent.llm.stream = True
    result = agent.crew.kickoff({"topic": "quantization"})
    for part in result:
        print(part)
        print("\n\n")
