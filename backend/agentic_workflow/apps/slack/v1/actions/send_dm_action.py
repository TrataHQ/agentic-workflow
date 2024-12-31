from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx

class SendDirectMessageAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Send a message to a user",
            description="Send a message to a user",
            dataSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "title": "User ID"},
                    "message": {"type": "string", "title": "Message to be sent to the user."}
                },
                "required": ["user_id", "message"]
            },
            uiSchema={
                "user_id": {"ui:widget": "NextUITextField", "ui:placeholder": "User ID"},
                "message": {"ui:widget": "NextUITextareaField", "ui:placeholder": "Message to be sent to the user."}
            }
        )
        super().__init__(action)


    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials | None, data: Dict[str, Any]) -> Dict[str, Any]:
        if credentials is None:
            raise ValueError("Credentials are required to send a message to a user")

        user_id = data["user_id"]  # Slack user ID of the recipient
        message = data["message"]

        async with httpx.AsyncClient() as client:
            if credentials.credentialsType == "oauth":
                # Step 1: Open a direct message channel
                dm_response = await client.post(
                    "https://slack.com/api/conversations.open",
                    headers={"Authorization": f"Bearer {credentials.accessToken}"},
                    json={"users": user_id}
                )
                dm_data = dm_response.json()

                if not dm_data.get("ok"):
                    raise ValueError(f"Failed to open conversation: {dm_data.get('error')}")

                dm_channel = dm_data["channel"]["id"]

                # Step 2: Send the message
                response = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {credentials.accessToken}"},
                    json={"channel": dm_channel, "text": message}
                )
            else:
                raise ValueError("Invalid credentials type")
        
        return response.json()
