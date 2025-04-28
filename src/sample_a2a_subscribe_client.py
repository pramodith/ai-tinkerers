from a2a_min.client import TaskQueryParams
import uvicorn
from fastapi import FastAPI, Request
from a2a_min_subscribe_client import A2aMinSubscribeClient
from a2a_min.base.types import TaskPushNotificationConfig, PushNotificationConfig
import threading
import time
import asyncio
import logging
import json

logging.basicConfig(level=logging.INFO)  # or INFO, or ERROR
logger = logging.getLogger(__name__)
# 1. Start a FastAPI app to receive notifications
app = FastAPI()

@app.post("/notify")
async def notify(request: Request):
    data = await request.json()
    print(f"Received notification: {json.dumps(data, indent=4)}")
    return {"status": "received"}


# 2. Start the client and register the callback URL
async def start_client():
    # Replace with your actual server URL
    SERVER_URL = "http://localhost:8000/"
    NOTIFY_URL = "http://localhost:9000/notify"  # This must be reachable by the server

    # Connect and register notification callback
    client = A2aMinSubscribeClient.connect(SERVER_URL)
    logger.info("Client connected to server")
    task_id = await client.send_message("Hello, Echo Agent!")
    logger.info(f"Task ID: {task_id}")

    # Wait for a bit for the task to be created
    await asyncio.sleep(2)

    # Send the notification callback to the server
    push_notification_config = TaskPushNotificationConfig(
        id=task_id, pushNotificationConfig=PushNotificationConfig(url=NOTIFY_URL)
    )
    logger.info("Configuring a Notification Url.")
    await client._client.set_task_callback(push_notification_config)
    print(f"Client registered with notification callback: {NOTIFY_URL}")


if __name__ == "__main__":
    # Start the notification server in a background thread/process
    threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=9000), daemon=True
    ).start()

    # Start the client
    asyncio.run(start_client())

    # Keep the main thread alive to receive notifications
    print("Client and notification server running. Waiting for notifications...")
    while True:
        time.sleep(60)
