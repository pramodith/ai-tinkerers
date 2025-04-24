from a2a_min.task_manager import A2aMinTaskManager
from a2a_min.base.types import (
    SendTaskRequest,
    SendTaskResponse,
    TaskStatus,
    TaskState,
    Artifact,
    PushNotificationConfig
)
from a2a_min.agent_adapter import AgentAdapter

import asyncio
import httpx
import logging
import time

logger = logging.getLogger(__name__)


class A2aMinSubscribeTaskManager(A2aMinTaskManager):
    """
    A custom task manager that extends the default task manager to support task notifications.
    """
    def __init__(self, agent: AgentAdapter):
        super().__init__(agent)

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handle a send task request.

        Args:
            request: The send task request.

        Returns:
            A response containing the result of the task.
        """
        # Add the task to the store
        await self.upsert_task(request.params)
        print(f"In send task {time.time()}")
        task = await self.update_store(
            request.params.id, TaskStatus(state=TaskState.SUBMITTED), None
        )
        print(f"In send task {self.tasks}")
        # Non-blocking call to start the task
        asyncio.create_task(self.start_task(request))
        return SendTaskResponse(id=request.id, result=task)
      

    async def start_task(self, request: SendTaskRequest) -> None:
        """
        Starts the task by calling the agent's invoke method.
        Once the task is complete the result is sent to the client's notification
        url.
        """
        logger.info(f"Starting task {request.params.id}")
        # Update task status to Working
        await self.update_store(
            request.params.id, TaskStatus(state=TaskState.WORKING), None
        )
        # Get the user query
        query = self._get_user_query(request.params)
        
        # Call the agent's invoke method
        try:
            agent_result = await self.agent.invoke(query, request.params.sessionId)

            artifact = None
            task_status = None

            if agent_result.requires_input:
                task_status = TaskStatus(
                    state=TaskState.INPUT_REQUIRED, message=agent_result.message
                )
            else:
                task_status = TaskStatus(state=TaskState.COMPLETED)
                artifact = Artifact(parts=agent_result.message.parts)
            
            # Update task status
            task = await self.update_store(
                request.params.id, task_status, None if artifact is None else [artifact]
            )
            
            # Append task history
            task_result = self.append_task_history(task, request.params.historyLength)
            # Get the notification config
            notif_config = await self.get_push_notification_info(request.params.id)
            if notif_config:
                # Send the notification
                await self.send_notification(request.params.id, artifact)
            else:
                return SendTaskResponse(id=request.id, result=task_result)

        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise ValueError(f"Error invoking agent: {e}")

    async def send_notification(self, task_id: str, artifact: Artifact):
        notif_config = await self.get_push_notification_info(task_id)
        url = notif_config.url
        # Send a push notification to the user
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(
                    url, json=artifact.model_dump(), headers=None
                )
                response.raise_for_status()
                logger.info(f"Push-notification sent for URL: {url}")
            except Exception as e:
                logger.warning(
                    f"Error during sending push-notification for URL {url}: {e}"
                )
    
    async def set_push_notification_info(self, task_id: str, notification_config: PushNotificationConfig):
        print(f"In set push {time.time()}")
        async with self.lock:
            for _ in range(3):
                task = self.tasks.get(task_id)
                if task is None:
                    print(f"Tasks are {self.tasks}")
                    await asyncio.sleep(1)
                else:
                    break

            if task is None:
                raise ValueError(f"Task: {task_id} not found.")
            
            self.push_notification_infos[task_id] = notification_config

        return

    async def get_push_notification_info(self, task_id: str) -> PushNotificationConfig:
        async with self.lock:
            for _ in range(3):
                task = self.tasks.get(task_id)
                if task is None:
                    await asyncio.sleep(1)

            if task is None:
                raise ValueError(f"Task: {task_id} not found.")

            return self.push_notification_infos[task_id]
            