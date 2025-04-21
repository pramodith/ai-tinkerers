from a2a_min.middleware import LoggingMiddleware
from a2a_min import AgentAdapter, A2aMinServer, AgentInvocationResult
from a2a_min.base.types import (
    AgentAuthentication,
    AgentCard,
    AgentCapabilities, 
    AgentSkill, 
)
from ai_news_riddle_agent import AINewsRiddleAgent

import asyncio

class AINewsRiddleAgentAdapter(AgentAdapter):
    """
    An agent that creates riddles based on the latest AI news.
    """
    def __init__(self):
        self.agent = AINewsRiddleAgent()
        super().__init__()
    
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def description(self):
        return self.__class__.__doc__

    @property
    def supported_content_types(self):
        return ["text"]

    @property
    def capabilities(self):
        return AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=False
        )

    @property
    def skills(self):
        return [
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
        self.agent.llm.stream = False
        response = self.agent.crew.kickoff({"topic": query})
        agent_response = AgentInvocationResult.agent_msg(
            response.raw,
        )
        return agent_response
    
    async def async_invoke(self, query: str) -> AgentInvocationResult:
        return await self.agent.crew.kickoff_async({"topic": query})
    
    async def stream(self, query: str, session_id: str):
        """Stream a response to a query.
        
        Default implementation yields the invoke result.
        
        Args:
            query: The user's query.
            session_id: A unique identifier for the session.
            
        Yields:
            AgentInvocationResult objects containing parts of the agent's response.
        """
        self.agent.llm.stream = True
        response = await self.async_invoke(query)
        response = response.raw
        for word in response.split():
            result = AgentInvocationResult.agent_msg(f"{word} ")
            result.is_complete = False
            yield result
            await asyncio.sleep(0.05)
        response = AgentInvocationResult.agent_msg(response)
        response.is_complete = True
        yield response
        
if __name__ == "__main__":
    # Start the AINewsRiddleAgent server
    A2aMinServer.from_agent(AINewsRiddleAgentAdapter(), middlewares=[LoggingMiddleware()]).start()
