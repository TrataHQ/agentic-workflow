from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx


class GetContactAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Get contact details",
            description="Get the contact details of a contact stored in Trata platform",
            dataSchema={
                "title": "Contact details",
                "type": "object",
                "properties": {
                    "oneOf": [
                        {
                            "contactId": {
                                "type": "string",
                                "title": "Contact ID",
                                "description": "The ID of the contact",
                            }
                        },
                        {
                            "contactEmail": {
                                "type": "string",
                                "title": "Contact Email",
                                "description": "The email of the contact",
                                "format": "email",
                            }
                        },
                        {
                            "contactPhone": {
                                "type": "string",
                                "title": "Contact Phone",
                                "description": "The phone of the contact",
                                "format": "tel",
                            }
                        },
                    ]
                },
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
            raise ValueError("Credentials are required to get contact details")

        contactId = data["contactId"]
        contactEmail = data["contactEmail"]
        contactPhone = data["contactPhone"]
        # TODO: Add actual Trata API call here
        if credentials.credentialsType == "apikey":
            api_key = credentials.apiKey
            http_client = httpx.AsyncClient()
            # async call to Trata API
            if contactId is not None:
                async with http_client.stream(
                    "GET",
                    f"https://api.trata.ai/v1/prospects/{contactId}",
                    headers={"Authorization": f"Bearer {api_key}"},
                ) as response:
                    response.raise_for_status()
                    contact_data = await response.json()
            elif contactEmail is not None:
                async with http_client.stream(
                    "GET",
                    f"https://api.trata.ai/v1/prospects?email={contactEmail}",
                    headers={"Authorization": f"Bearer {api_key}"},
                ) as response:
                    response.raise_for_status()
                    contact_data = await response.json()
            elif contactPhone is not None:
                async with http_client.stream(
                    "GET",
                    f"https://api.trata.ai/v1/prospects?phone={contactPhone}",
                    headers={"Authorization": f"Bearer {api_key}"},
                ) as response:
                    response.raise_for_status()
                    contact_data = await response.json()
            return contact_data
        else:
            raise ValueError("Invalid credentials type")
