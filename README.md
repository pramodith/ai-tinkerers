# ai-tinkerers-a2a-demo

A playground for experimenting with Google A2A (Agent-to-Agent) patterns, agent adapters, streaming, and push notification/callback workflows in Python.

## A2A Example Types

### 1. Basic Echo Agent/Server
- **Files:** `sample_a2a_subscribe_server.py`, `sample_a2a_subscribe_client.py`
- **Description:** Minimal agent/server that echoes user queries. Demonstrates basic A2A server and client setup.

### 2. Push Notification/Callback (Subscribe) Example
- **Files:**
  - `sample_a2a_subscribe_server.py` (with custom task manager)
  - `sample_a2a_subscribe_client.py` (with FastAPI notification endpoint)
  - `a2a_min_subscribe_task_manager.py`, `a2a_min_subscribe_client.py`
- **Description:** Shows how a client can register a callback URL to receive asynchronous notifications from the server when tasks complete. Illustrates non-blocking task execution and HTTP callbacks.

### 3. Advanced News Riddle Agent
- **Files:** `news_riddle_agent.py`, `news_riddle_server.py`, `news_riddle_client.py`, `gradio_app.py`
- **Description:**
    - An advanced agent that generates riddles based on the latest news headlines, not just AI news. It uses LLMs and a web search tool to find recent news, then creates riddles and answers for them.
    - The agent is composed of two sub-agents: a news search agent and a riddle creation agent. The workflow is orchestrated via a CrewAI `Crew` object with two tasks: one for news search, one for riddle creation.
    - Example usage (from `news_riddle_agent.py`):
      ```python
      agent = AINewsRiddleAgent()
      agent.llm.stream = False
      result = agent.crew.kickoff({"topic": "tarrifs"})
      for part in result:
          print(part)
      ```
    - The agent and tasks are now more general ("news" not just "AI news").
    - Supports both streaming and non-streaming LLM output.

## Setup
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run `uv sync`
3. Run the server/client of your choice by running `uv run src/<file>.py`

## Running Examples
- See each script for specific instructions and requirements (e.g., FastAPI, Uvicorn for notification callback, Gradio for web UI).
- Make sure to set up any required environment variables (API keys, etc.).

---

*This repo is intended for prototyping and learning about agent-to-agent workflows, streaming, and async notification patterns in Python.*