from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx

class HttpAction(AppActionExecutor):
    def __init__(self):
        step = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="http",
            description="HTTP request action",
            dataSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to send the HTTP request to",
                        "title": "Endpoint URL"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method to use",
                        "title": "HTTP Method"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP headers to send with the request",
                        "title": "HTTP Headers"
                    },
                    "body": {
                        "type": "object",
                        "description": "Body of the HTTP request",
                        "title": "HTTP Body"
                    }
                }
            },
            uiSchema={
                "url": {
                    "ui:widget": "NextUITextField",
                    "ui:placeholder": "https://example.com/api/v1/endpoint"
                },
                "method": {
                    "ui:widget": "NextUISelectField",
                    "ui:options": {"enum": ["GET", "POST", "PUT", "DELETE"]},
                    "ui:placeholder": "GET"
                },
                "headers": {
                    "ui:widget": "NextUITextareaField",
                    "ui:placeholder": "Headers to send with the request"
                },
                "body": {
                    "ui:widget": "NextUITextareaField",
                    "ui:placeholder": "Body of the HTTP request"
                }
            }
        )
        super().__init__(step)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        # Add query params to url
        if context.request is not None:
            data["url"] = f"{data['url']}?{context.request.query_params}"

        httpx_client = httpx.AsyncClient()
        async with httpx_client:
            response = await httpx_client.request(data["method"], data["url"], headers=data["headers"], json=data["body"])
        return response.json()
