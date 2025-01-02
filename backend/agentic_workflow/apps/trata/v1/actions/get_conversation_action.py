from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx


class GetConversationAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Get conversation details",
            description="Get the conversation details of a conversation stored in Trata platform",
            dataSchema={
                "title": "Conversation details",
                "type": "object",
                "properties": {
                    "conversationId": {
                        "type": "string",
                        "title": "Conversation ID",
                        "description": "The ID of the conversation",
                    },
                },
                "required": ["conversationId"],
            },
            uiSchema={
                "contactId": {
                    "ui:widget": "NextUITextField",
                    "ui:placeholder": "Contact ID",
                },
                "contactEmail": {
                    "ui:widget": "NextUITextField",
                    "ui:placeholder": "Contact Email",
                },
                "contactPhone": {
                    "ui:widget": "NextUITextField",
                    "ui:placeholder": "Contact Phone",
                },
            },
            uiNodeType=UiNodeType.ACTION,
        )
        super().__init__(action)

    async def run(
        self,
        context: StepContext,
        app: AppDefinition,
        credentials: AppCredentials | None,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        if credentials is None:
            raise ValueError("Credentials are required to get conversation details")

        conversationId = data["conversationId"]
        if credentials.credentialsType == "apikey":
            api_key = credentials.apiKey
            http_client = httpx.AsyncClient()
            # async call to Trata API
            if conversationId is not None:
                async with http_client.stream(
                    "GET",
                    f"https://api.trata.ai/v1/conversations/{conversationId}",
                    headers={"Authorization": f"Bearer {api_key}"},
                ) as response:
                    response.raise_for_status()
                    conversation_data = await response.json()
                return conversation_data
            else:
                raise ValueError(
                    f"Invalid inputs for getting conversation details {conversationId}"
                )
        else:
            raise ValueError("Invalid credentials type")
