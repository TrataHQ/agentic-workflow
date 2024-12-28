from typing import Any, Dict
from src.adk.models.executors import AppActionExecutor, StepContext
from src.adk.models.app import AppActionEntity, AppActionType
from src.adk.models.connection import AppCredentials
from src.adk.models.app_definition import AppDefinition

class SendMessageAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="send_message",
            description="Send a message to a channel",
            dataSchema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["channel", "message"]
            },
            uiSchema={
                "channel": {"ui:widget": "select"},
                "message": {"ui:widget": "textarea"}
            }
        )
        super().__init__(action)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        channel = context.input_data["channel"]
        message = context.input_data["message"]
        # TODO: Add actual Slack API call here
        return {"message_id": "dummy_message_id"}
