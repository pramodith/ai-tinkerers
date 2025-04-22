import gradio as gr
import json
from openai import AsyncOpenAI

from news_riddle_client import AINewsRiddleClient
from dotenv import load_dotenv
from logging import getLogger

logger = getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
OPENAI_MODEL = "gpt-4.1-nano"

# Riddle server endpoint (assuming it's running locally)
RIDDLE_SERVER_URL = "http://localhost:8000/"  # Adjust if needed
client = AINewsRiddleClient.connect(RIDDLE_SERVER_URL)
openai_client = AsyncOpenAI()


# Helper: Detect if user is asking for a riddle
async def is_riddle_request(message: str) -> str:
    triggers = ["riddle", "puzzle", "give me a riddle", "ai riddle"]
    if any(trigger in message.lower() for trigger in triggers):
        extract_topic_message = [
            {
                "role": "user",
                "content": f"Extract the topic from the message. {message}",
            }
        ]
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


async def stream_openai_response(messages):
    try:
        response = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, stream=True
        )
        async for chunk in response:
            if chunk and len(chunk.choices) > 0:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"[OpenAI API error: {e}]"


# Call OpenAI GPT-4.1-nano
async def get_openai_response(messages):
    try:
        completion = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, stream=False
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
        response = await get_openai_response([{"role": "user", "content": message}])
        return response, None, None


async def stream_chatbot_fn(message):
    topic = await is_riddle_request(message)
    if topic:
        print(f"Topic: {topic}")
        async for update in client.send_message_streaming(topic):
            if update.artifact and update.artifact.parts:
                artifact = update.artifact.parts[0]
                if artifact and hasattr(artifact, "text") and update.status:
                    if update.is_final:
                        yield ""
                        break
                    yield artifact.text
    else:
        async for partial_response in stream_openai_response(
            [{"role": "user", "content": message}]
        ):
            yield partial_response


with gr.Blocks() as demo:
    gr.Markdown("# AI Chatbot (GPT-4.1-nano)\nAsk anything, or request a riddle!")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear")
    do_stream = gr.Checkbox(label="Stream response", value=False)

    async def respond(user_message, chat_history, do_stream):
        if do_stream:
            response = ""
            print("in do stream")
            async for partial_response in stream_chatbot_fn(user_message):
                if partial_response:
                    response += partial_response
                    chat_history_display = chat_history + [[user_message, response]]
                    yield "", chat_history_display
            # Optionally, yield the final cleaned-up response one last time
            response = response.strip()
            response = json.dumps(response, indent=2)
            chat_history_display = chat_history + [[user_message, response]]
            yield "", chat_history_display
        else:
            response, task_id, session_id = await chatbot_fn(user_message, chat_history)
            if task_id and session_id:
                response = f"Task ID: {task_id}, Session ID: {session_id}\n{response}"

        chat_history = chat_history + [[user_message, response]]
        yield "", chat_history

    msg.submit(respond, [msg, chatbot, do_stream], [msg, chatbot])
    clear.click(lambda: ("", []), None, [msg, chatbot])

demo.launch(share=True)
