import asyncio
import gradio as gr
import openai

from a2a_min import A2aMinClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
OPENAI_MODEL = "gpt-4.1-nano"

# Riddle server endpoint (assuming it's running locally)
RIDDLE_SERVER_URL = "http://localhost:8000/"  # Adjust if needed

# Helper: Detect if user is asking for a riddle
def is_riddle_request(message: str) -> bool:
    triggers = ["riddle", "puzzle", "give me a riddle", "ai riddle"]
    return any(trigger in message.lower() for trigger in triggers)

# Call riddle server
async def get_riddle_from_server(message: str):
    try:
        client = A2aMinClient.connect("http://localhost:8000/")
        task = await client.send_message(message)
        if task.artifacts:
            artifact = task.artifacts[-1]
            return artifact.model_dump()
        else:
            return f"[Riddle server error: {resp.status_code}]"
    except Exception as e:
        return f"[Could not reach riddle server: {e}]"

# Call OpenAI GPT-4.1-nano
def get_openai_response(message: str):
    try:
        completion = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": message}],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI API error: {e}]"

def chatbot_fn(message, history):
    if is_riddle_request(message):
        return asyncio.run(get_riddle_from_server(message))
    else:
        return get_openai_response(message)

with gr.Blocks() as demo:
    gr.Markdown("# AI Chatbot (GPT-4.1-nano)\nAsk anything, or request a riddle!")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear")

    def respond(user_message, chat_history):
        response = chatbot_fn(user_message, chat_history)
        chat_history = chat_history + [[user_message, response]]
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: ("", []), None, [msg, chatbot])

demo.launch()
