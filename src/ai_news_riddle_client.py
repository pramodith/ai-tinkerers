import asyncio
import gradio as gr
import openai

from a2a_min import A2aMinClient
from dotenv import load_dotenv
from logging import getLogger

logger = getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
OPENAI_MODEL = "gpt-4.1-nano"

# Riddle server endpoint (assuming it's running locally)
RIDDLE_SERVER_URL = "http://localhost:8000/"  # Adjust if needed
client = A2aMinClient.connect(RIDDLE_SERVER_URL)
# Helper: Detect if user is asking for a riddle
async def is_riddle_request(message: str) -> str:
    triggers = ["riddle", "puzzle", "give me a riddle", "ai riddle"]
    if any(trigger in message.lower() for trigger in triggers):
        extract_topic_message = [{"role": "user", "content": f"Extract the topic from the message. {message}"}]
        topic = await get_openai_response(extract_topic_message)
        return topic
    return ""
     
# Call riddle server
async def get_riddle_from_server(message: str):
    try:
        task = await client.send_message(message)
        if task.artifacts:
            artifact = task.artifacts[-1]
            return artifact.model_dump()
        else:
            return "[Riddle server error: No artifacts]"
    except Exception as e:
        return f"[Could not reach riddle server: {e}]"

# Call OpenAI GPT-4.1-nano
async def get_openai_response(messages):
    try:
        completion = await asyncio.to_thread(
            openai.chat.completions.create,
            model=OPENAI_MODEL,
            messages=messages
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI API error: {e}]"

async def chatbot_fn(message, history):
    topic = await is_riddle_request(message)
    if topic:
        task = await client.send_message(topic)
        if task.artifacts:
            artifact = task.artifacts[-1]
            part = artifact.parts[-1]
            if hasattr(part, "text"):
                response = part.text
        return response, task.id, task.sessionId
    else:
        response = await get_openai_response([{ "role": "user", "content": message }])
        return response, None, None

with gr.Blocks() as demo:
    gr.Markdown("# AI Chatbot (GPT-4.1-nano)\nAsk anything, or request a riddle!")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear")

    async def respond(user_message, chat_history):
        response, task_id, session_id = await chatbot_fn(user_message, chat_history)
        if task_id and session_id:
            response = f"Task ID: {task_id}, Session ID: {session_id}\n{response}"
        chat_history = chat_history + [[user_message, response]]
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: ("", []), None, [msg, chatbot])

demo.launch(share=True)
