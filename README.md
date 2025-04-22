# ai-tinkerers

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

### 3. Advanced AI News Riddle Agent
- **Files:** `ai_news_riddle_agent.py`, `ai_news_riddle_server.py`, `ai_news_riddle_client.py`, `gradio_app.py`
- **Description:** A more complex agent that generates AI news riddles using LLMs, web search, and streaming. Supports both streaming and non-streaming modes in the UI.

## Setup
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run `uv sync`
3. Run the server/client of your choice by running `uv run src/<file>.py`

## Running Examples
- See each script for specific instructions and requirements (e.g., FastAPI, Uvicorn for notification callback, Gradio for web UI).
- Make sure to set up any required environment variables (API keys, etc.).

---

*This repo is intended for prototyping and learning about agent-to-agent workflows, streaming, and async notification patterns in Python.*