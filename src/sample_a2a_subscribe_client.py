import uvicorn
from fastapi import FastAPI, Request
from a2a_min_subscribe_client import A2aMinSubscribeClient
from a2a_min.base.types import TaskPushNotificationConfig, PushNotificationConfig
import threading
import time
import asyncio

# 1. Start a FastAPI app to receive notifications
app = FastAPI()

@app.post("/notify")
async def notify(request: Request):
    data = await request.json()
    print(f"Received notification: {data}")
    return {"status": "received"}


# 2. Start the client and register the callback URL
async def start_client():
    # Replace with your actual server URL
    SERVER_URL = "http://localhost:8000/"
    NOTIFY_URL = "http://localhost:9000/notify"  # This must be reachable by the server

    # Connect and register notification callback
    client = A2aMinSubscribeClient.connect(SERVER_URL)
    print("Client connected to server")
    task_id = await client.send_message("Hello, Echo Agent!")
    print(f"Task ID: {task_id}")
    push_notification_config = TaskPushNotificationConfig(
        id=task_id, pushNotificationConfig=PushNotificationConfig(url=NOTIFY_URL)
    )
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
