import gradio as gr
import json
from openai import AsyncOpenAI

from news_riddle_client import AINewsRiddleClient
from dotenv import load_dotenv
from logging import getLogger
import logging

logging.basicConfig(level=logging.WARNING)  # or INFO, or ERROR

logger = getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
OPENAI_MODEL = "gpt-4.1"

# Riddle server endpoint (assuming it's running locally)
RIDDLE_SERVER_URL = "http://localhost:8000/"  # Adjust if needed
logger.warning("Getting the Agent Card!")
client = AINewsRiddleClient.connect(RIDDLE_SERVER_URL)
openai_client = AsyncOpenAI()


# Helper: Detect if user is asking for a riddle
async def is_riddle_request(message: str) -> str:
    """
    Determines if the user's message is a request for a riddle.
    If so, extracts the topic from the message using OpenAI.

    Args:
        message (str): The user's input message.

    Returns:
        str: The extracted topic if a riddle is requested, otherwise an empty string.
    """
    triggers = ["riddle", "puzzle", "give me a riddle", "ai riddle"]
    # Check if any trigger word is present in the message
    if any(trigger in message.lower() for trigger in triggers):
        extract_topic_message = [
            {
                "role": "user",
                "content": f"Extract the topic from the message. {message} and do nothing else. "
                           "Do not include any additional words beyond the topic.",
            }
        ]
        # Use OpenAI to extract the topic
        topic = await get_openai_response(extract_topic_message)
        return topic
    return ""


# Call riddle server
async def get_riddle_from_server(message: str):
    """
    Sends a message to the riddle server and retrieves the response.

    Args:
        message (str): The message or topic to send to the riddle server.

    Returns:
        dict or str: The artifact data from the riddle server, or an error message.
    """
    try:
        # Send the message to the riddle server
        task = await client.send_message(message)
        if task.artifacts:
            artifact = task.artifacts[-1]
            return artifact.model_dump()  # Return the latest artifact as a dictionary
        else:
            return "[Riddle server error: No artifacts]"
    except Exception as e:
        return f"[Could not reach riddle server: {e}]"


async def stream_openai_response(messages: list[dict[str, str]]):
    """
    Streams a response from the OpenAI API for the given messages.

    Args:
        messages (list): List of message dicts for OpenAI chat completion.

    Yields:
        str: Partial responses as they are received from OpenAI.
    """
    try:
        # Request streaming chat completion from OpenAI
        response = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, stream=True
        )
        async for chunk in response:
            if chunk and len(chunk.choices) > 0:
                yield chunk.choices[0].delta.content  # Yield each part of the response
    except Exception as e:
        yield f"[OpenAI API error: {e}]"


# Call OpenAI GPT-4.1-nano
async def get_openai_response(messages: list[dict[str, str]]):
    """
    Gets a non-streaming response from the OpenAI API for the given messages.

    Args:
        messages (list): List of message dicts for OpenAI chat completion.

    Returns:
        str: The response content from OpenAI, or an error message.
    """
    try:
        # Request a single chat completion from OpenAI
        completion = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, stream=False
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI API error: {e}]"


async def chatbot_fn(message, history):
    """
    Main chatbot logic to handle user messages, determining if a riddle is requested or if a general AI response is needed.

    Args:
        message (str): The user's input message.
        history (list): The chat history (not used in logic, but available for future use).

    Returns:
        tuple: (response text, task_id, session_id) if a riddle, otherwise (response, None, None).
    """
    topic = await is_riddle_request(message)
    logger.warning("Creating a new task!")
    if topic:
        # If a riddle is requested, send the topic to the riddle server
        task = await client.send_message(topic)
        logger.warning(f"Created Task : {task}")
        if task.artifacts:
            artifact = task.artifacts[-1]
            part = artifact.parts[-1]
            if hasattr(part, "text"):
                response = part.text
        return response, task.id, task.sessionId
    else:
        # Otherwise, get a general response from OpenAI
        response = await get_openai_response([{"role": "user", "content": message}])
        return response, None, None


async def stream_chatbot_fn(message):
    """
    Handles streaming chatbot responses, either from the riddle server or OpenAI, 
    depending on the user's request.

    Args:
        message (str): The user's input message.

    Yields:
        str: Partial responses as they are received.
    """
    topic = await is_riddle_request(message)
    if topic:
        logger.warning("Creating a new task!")
        # Stream updates from the riddle server
        async for update in client.send_message_streaming(topic):
            if update.artifact and update.artifact.parts:
                artifact = update.artifact.parts[0]
                if artifact and hasattr(artifact, "text") and update.status:
                    if update.is_final:
                        yield ""  # End of stream
                        break
                    yield artifact.text
    else:
        # Stream responses from OpenAI
        async for partial_response in stream_openai_response(
            [{"role": "user", "content": message}]
        ):
            yield partial_response

def format_riddle(riddles: dict):
    """
    Formats a riddle response for display, combining riddles, answers, and hints.

    Args:
        riddles (dict): Dictionary with keys 'riddles', 'answers', and 'hints'.

    Returns:
        str: Formatted string for display.
    """
    formatted_responses = ""
    # Combine each riddle, answer, and hint into a readable format
    for riddle, answer, hint in zip(riddles["riddles"], riddles["answers"], riddles["hints"]):
        formatted_responses += f"Riddle: {riddle}\nAnswer: {answer}\nHint: {hint}\n\n"
    return formatted_responses.rstrip()

with gr.Blocks() as demo:
    gr.Markdown("# Riddler \nAsk anything, or request a riddle!")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear")
    do_stream = gr.Checkbox(label="Stream response", value=False)

    async def respond(user_message, chat_history, do_stream):
        """
        Handles the response logic for the Gradio UI, supporting both streaming and non-streaming modes.

        Args:
            user_message (str): The user's input message.
            chat_history (list): The chat history as a list of [user, bot] pairs.
            do_stream (bool): Whether to stream the response or not.

        Yields:
            tuple: (empty string for textbox, updated chat history)
        """
        task_id = None
        session_id = None

        if do_stream:
            # Stream the chatbot response and update the chat history incrementally
            response = ""
            async for partial_response in stream_chatbot_fn(user_message):
                if partial_response:
                    response += partial_response
                    chat_history_display = chat_history + [[user_message, response]]
                    yield "", chat_history_display         
        else:
            # Get the full chatbot response
            response, task_id, session_id = await chatbot_fn(user_message, chat_history)
            
        try:
            # Attempt to parse the response as JSON and format it if possible
            response = response.strip()
            response = json.loads(response)
            response = format_riddle(response)
        except Exception as e:
            logger.error(f"Failed to parse response as json: {e}")
            print(response)
        
        if task_id and session_id:
            # If a riddle was generated, include task and session IDs
            response = f"Task ID: {task_id}, Session ID: {session_id}\n{response}"

        chat_history_display = chat_history + [[user_message, response]]
        yield "", chat_history_display

    msg.submit(respond, [msg, chatbot, do_stream], [msg, chatbot])
    clear.click(lambda: ("", []), None, [msg, chatbot])

demo.launch(share=True)
