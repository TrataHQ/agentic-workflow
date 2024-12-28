from typing import Any, Dict
from src.adk.models.executors import AppActionExecutor, StepContext
from src.adk.models.app_definition import AppDefinition
from src.adk.models.connection import AppCredentials
from src.adk.models.app import AppActionEntity, AppActionType
class NewMessageTrigger(AppActionExecutor):
    def __init__(self):
        trigger = AppActionEntity(
            actionType=AppActionType.TRIGGER,
            name="new_message",
            description="Triggered when a new message is posted",
            dataSchema={
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "message": {"type": "string"}
                }
            },
            uiSchema={
                "channel": {"ui:widget": "select"}
            }
        )
        super().__init__(trigger)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        if context.request is None:
            raise ValueError("Request is required for triggers.")
        # TODO: Add request authentication.
        body = await context.request.json()
        channel = body["channel"]
        message = body["message"]

        return {
            "channel": channel,
            "message": message
        }
