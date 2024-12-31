from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType

class WebhookTrigger(AppActionExecutor):
    def __init__(self):
        trigger = AppActionEntity(
            actionType=AppActionType.TRIGGER,
            name="Webhook Trigger",
            description="Webhook trigger endpoint",
            uiSchema={},
            dataSchema={}
        )
        super().__init__(trigger)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        if context.request is None and data is None:
            raise ValueError("Request or input data is required for triggers.")

        headers = context.request.headers if context.request is not None else data.get("headers", {})
        query_params = context.request.query_params if context.request is not None else data.get("query_params", {})
        body = context.request.json() if context.request is not None else data.get("body", {})

        # Validate authentication
        auth_header = headers.get("authorization")
        if not auth_header:
            raise ValueError("Authorization header is missing")

        if credentials.credentialsType == "basic":
            # Validate Basic auth
            import base64
            expected_auth = f"{credentials.username}:{credentials.password}"
            expected_header = f"Basic {base64.b64encode(expected_auth.encode()).decode()}"
            if auth_header != expected_header:
                raise ValueError("Invalid Basic authentication credentials")
        elif credentials.credentialsType == "apikey":
            # Validate Bearer token using API key
            expected_header = f"Bearer {credentials.apiKey}"
            if auth_header != expected_header:
                raise ValueError("Invalid Bearer token")
        else:
            # No authentication required
            pass

        return {
            "headers": headers,
            "query_params": query_params,
            "body": body
        }
