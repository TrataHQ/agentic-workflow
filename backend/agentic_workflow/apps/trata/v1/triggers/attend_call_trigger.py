from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx

class AttendCallTrigger(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.TRIGGER,
            name="Attend a call",
            description="Trigger for Trata AI to attend a call",
            dataSchema={
                "title": "Attend a call",
                "type": "object",
                "properties": {
                    "agentId": {
                        "type": "string",
                        "title": "Trata Agent ID",
                        "description": "The ID of the agent which is attending the call",
                    }
                },
                "required": ["agentId"]
            },
            uiSchema={
                "agentId": {"ui:widget": "NextUITextField", "ui:placeholder": "Agent ID"},
            },
            uiNodeType=UiNodeType.Subflow
        )
        super().__init__(action)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials | None, data: Dict[str, Any]) -> Dict[str, Any]:
        if credentials is None:
            raise ValueError("Credentials are required to attend a call")

        agentId = data["agentId"]
        # TODO: Add actual Trata API call here
        if credentials.credentialsType == "apikey":
            api_key = credentials.apiKey
            http_client = httpx.AsyncClient()
            # async call to Trata API
            if agentId is not None:
                # async with http_client.stream("POST", f"https://api.trata.ai/v1/agents/{agentId}/attend", headers={"Authorization": f"Bearer {api_key}"}) as response:
                #     response.raise_for_status()
                #     call_data = await response.json()
                #     return call_data
                return data
            else:
                raise ValueError(f"Invalid inputs for attending a call {agentId}")
        else:
            raise ValueError("Invalid credentials type")
