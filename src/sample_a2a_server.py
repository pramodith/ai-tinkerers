from a2a_min import AgentAdapter, A2aMinServer, AgentInvocationResult

class EchoAgent(AgentAdapter):
    """ A simple echo agent that repeats the user's message """
    def invoke(self, query: str, session_id: str) -> AgentInvocationResult:
        """Echo back the user's query."""
        return AgentInvocationResult.agent_msg(f"Echo: {query}")

if __name__ == "__main__":
    # Start the echo agent server
    A2aMinServer.from_agent(EchoAgent()).start()