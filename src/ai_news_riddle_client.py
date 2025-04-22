from a2a_min import A2aMinClient
from uuid import uuid4
from typing import Optional, List, AsyncIterable
from a2a_min.base.types import Message, TextPart, Artifact, TaskSendParams
from a2a_min.types import TaskUpdate


class AINewsRiddleClient(A2aMinClient):
    """
    A client for interacting with the AI News Riddle agent.

    This client is designed to send messages to the AI News Riddle agent and receive responses.
    It uses the A2aMinClient as a base class for simplified communication with A2A servers.
    """

    def __init__(self, url: str):
        super().__init__(url)

    async def send_message_streaming(
        self,
        message: str,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        accepted_output_modes: Optional[List[str]] = None,
    ) -> AsyncIterable[TaskUpdate]:
        """Send a message to the agent and get a streaming response.

        Args:
            message: The message to send.
            session_id: An optional session ID. If not provided, a new one will be generated.
            task_id: An optional task ID. If not provided, a new one will be generated.
            accepted_output_modes: Optional list of accepted output modes.

        Yields:
            TaskUpdate objects containing parts of the agent's response.
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

        async for update in self._client.send_task_streaming(params):
            if hasattr(update.result, "status"):
                status_update = update.result
                if status_update.status.message:
                    artifact = Artifact(
                        parts=status_update.status.message.parts, index=0, append=False
                    )
                else:
                    artifact = None
                yield TaskUpdate(
                    status=status_update.status.state,
                    is_final=status_update.final,
                    metadata=status_update.metadata,
                    artifact=artifact,
                )
            elif hasattr(update.result, "artifact"):
                artifact_update = update.result
                yield TaskUpdate(
                    artifact=artifact_update.artifact, metadata=artifact_update.metadata
                )
