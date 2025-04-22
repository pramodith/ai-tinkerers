from typing import override, Optional, List
from uuid import uuid4
from a2a_min import A2aMinClient
from a2a_min.base.types import Task, Message, TextPart, TaskSendParams
from asyncio import create_task


class A2aMinSubscribeClient(A2aMinClient):
    def __init__(self, client: A2aMinClient):
        super().__init__(client)

    @override
    async def send_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        accepted_output_modes: Optional[List[str]] = None,
    ) -> Task:
        """Send a message to the agent and get a response.

        Args:
            message: The message to send.
            session_id: An optional session ID. If not provided, a new one will be generated.
            task_id: An optional task ID. If not provided, a new one will be generated.
            accepted_output_modes: Optional list of accepted output modes.

        Returns:
            A Task object containing the agent's response.
        """
        if session_id is None:
            session_id = uuid4().hex

        if task_id is None:
            task_id = uuid4().hex

        if accepted_output_modes is None:
            accepted_output_modes = ["text"]

        message_obj = Message(role="user", parts=[TextPart(text=message)])

        params = TaskSendParams(
            id=task_id,
            sessionId=session_id,
            message=message_obj,
            acceptedOutputModes=accepted_output_modes,
        )

        # Non-blocking call to create a new task
        create_task(self._client.send_task(params))
        # Return the task id to allow the client to subscribe for notifications
        return task_id
