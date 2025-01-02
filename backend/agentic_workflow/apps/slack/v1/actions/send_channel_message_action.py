from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx

class SendChannelMessageAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Send a message to a channel",
            description="Send a message to a channel",
            dataSchema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "title": "Channel Name"},
                    "message": {"type": "string", "title": "Message to be sent to the channel."}
                },
                "required": ["channel", "message"]
            },
            uiSchema={
                "channel": {"ui:widget": "NextUITextField", "ui:placeholder": "Channel Name"},
                "message": {"ui:widget": "NextUITextareaField", "ui:placeholder": "Message to be sent to the channel."}
            },
            uiNodeType=UiNodeType.Action
        )
        super().__init__(action)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials | None, data: Dict[str, Any]) -> Dict[str, Any]:
        if credentials is None:
            raise ValueError("Credentials are required to send a message to a channel")

        channel = data["channel"]
        message = data["message"]
        async with httpx.AsyncClient() as client:
            if credentials.credentialsType == "oauth":
                response = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {credentials.accessToken}"},
                    json={"channel": channel, "text": message}
                )
            else:
                raise ValueError("Invalid credentials type")
        return response.json()
