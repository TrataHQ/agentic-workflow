from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx

class MakeCallAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Dial a number",
            description="Dial a number and let Trata AI handle the call",
            dataSchema={
                "title": "Call request details",
                "type": "object",
                "properties": {
                    "phoneNumber": {
                        "type": "string",
                        "title": "Phone number",
                        "description": "The phone number to dial",
                        "format": "tel"
                    },
                    "agentId": {
                        "type": "string",
                        "title": "Trata Agent ID",
                        "description": "The ID of the agent to handle the call",
                    }
                },
                "required": ["phoneNumber", "agentId"]
            },
            uiSchema={
                "phoneNumber": {"ui:widget": "NextUITextField", "ui:placeholder": "Phone number"},
                "agentId": {"ui:widget": "NextUITextField", "ui:placeholder": "Agent ID"},
            },
            uiNodeType=UiNodeType.Subflow
        )
        super().__init__(action)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials | None, data: Dict[str, Any]) -> Dict[str, Any]:
        if credentials is None:
            raise ValueError("Credentials are required to make a call")

        phoneNumber = data["phoneNumber"]
        agentId = data["agentId"]
        # TODO: Add actual Trata API call here
        if credentials.credentialsType == "apikey":
            api_key = credentials.apiKey
            http_client = httpx.AsyncClient()
            # async call to Trata API
            if phoneNumber is not None and agentId is not None:
                async with http_client.stream("POST", f"https://api.trata.ai/v1/agents/{agentId}/dial?phoneNumber={phoneNumber}", headers={"Authorization": f"Bearer {api_key}"}) as response:
                    response.raise_for_status()
                    call_data = await response.json()
                    # TODO: This is an async API so poll the status of the call and wait for it to get completed.
                    return call_data
            else:
                raise ValueError(f"Invalid inputs for making a call {phoneNumber} and {agentId}")
        else:
            raise ValueError("Invalid credentials type")
