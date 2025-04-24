from a2a_min import AgentAdapter, A2aMinServer, AgentInvocationResult, Middleware
from a2a_min.base.server.server import A2AServer
from a2a_min.base.server.task_manager import TaskManager
from a2a_min_subscribe_task_manager import A2aMinSubscribeTaskManager

from typing import Optional, List
import time
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2AMinSubscribeServer(A2aMinServer):
    """
    Updates the from_agent function to use the custom task manager.
    """
    def __init__(
        self,
        server: A2AServer,
        task_manager: TaskManager,
        middlewares: Optional[List[Middleware]] = None,
    ):
        super().__init__(
            server=server, task_manager=task_manager, middlewares=middlewares
        )

    @classmethod
    def from_agent(
        cls,
        agent: AgentAdapter,
        host: str = "localhost",
        port: int = 8000,
        middlewares: Optional[List[Middleware]] = None,
    ) -> "A2aMinServer":
        """Create a server from an agent.

        Args:
            agent: The agent to serve.
            host: The host to bind to.
            port: The port to bind to.
            middlewares: Optional list of middleware to apply.

        Returns:
            An A2aMinServer instance configured with the agent.
        """
        url = f"http://{host}:{port}/"
        agent_card = agent.get_agent_card(url)
        task_manager = A2aMinSubscribeTaskManager(agent)

        server = A2AServer(
            agent_card=agent_card, task_manager=task_manager, host=host, port=port
        )

        return cls(server, task_manager, middlewares)


class EchoAgent(AgentAdapter):
    """A simple echo agent that repeats the user's message"""

    async def invoke(self, query: str, session_id: str) -> AgentInvocationResult:
        """Echo back the user's query."""
        await asyncio.sleep(10)
        return AgentInvocationResult.agent_msg(f"Echo: {query}")


if __name__ == "__main__":
    # Start the echo agent server
    A2AMinSubscribeServer.from_agent(EchoAgent()).start()
