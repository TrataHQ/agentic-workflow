from typing import Any, Dict
from src.adk.models.executors import AppActionExecutor, StepContext
from src.adk.models.app_definition import AppDefinition
from src.adk.models.connection import AppCredentials
from src.adk.models.app import AppActionEntity, AppActionType

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
        if context.request is None:
            raise ValueError("Request is required for triggers.")

        # Validate authentication
        auth_header = context.request.headers.get("authorization")
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

        headers = {k: v for k, v in context.request.headers.items()}
        query_params = {k: v for k, v in context.request.query_params.items()}
        body = await context.request.json()
        return {
            "headers": headers,
            "query_params": query_params,
            "body": body
        }
