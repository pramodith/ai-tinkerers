from a2a_min import AgentAdapter, A2aMinServer, AgentInvocationResult
from a2a_min.base.types import (
    AgentAuthentication,
    AgentCard,
    AgentCapabilities, 
    AgentSkill, 
)
from ai_news_riddle_agent import AINewsRiddleAgent

class AINewsRiddleAgentAdapter(AgentAdapter):
    """
    An agent that creates riddles based on the latest AI news.
    """

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.description = self.__class__.__doc__
        self.supported_content_types = ["text"]
        self.capabilities = AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=False
        )
        self.skills = [
            AgentSkill(
                id=f"{self.name.lower()}_skill",
                name=self.name,
                description=self.description,
                tags=["ai riddles", "ai puzzles"],
                examples=["AI riddle of the day", "AI puzzle of the day"]
            )
        ]
    
    def get_agent_card(self, url: str = "http://localhost:8000/") -> AgentCard:
        """Generate an agent card for this agent."""
        return AgentCard(
            authentication=None,
            name=self.name,
            version = "0.0.1",
            description=self.description,
            supported_content_types=self.supported_content_types,
            capabilities=self.capabilities,
            skills=self.skills,
            url=url,
            defaultInputModes = self.supported_content_types,
            defaultOutputModes = self.supported_content_types,
        )
    
    def invoke(self, query: str, session_id: str) -> AgentInvocationResult:
        agent = AINewsRiddleAgent()
        return agent.crew.kickoff(query)
        
if __name__ == "__main__":
    # Start the AINewsRiddleAgent server
    A2aMinServer.from_agent(AINewsRiddleAgentAdapter()).start()
