from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType


class WebhookTrigger(AppActionExecutor):
    def __init__(self):
        trigger = AppActionEntity(
            actionType=AppActionType.TRIGGER,
            name="Webhook Trigger",
            description="Webhook trigger endpoint",
            uiSchema={},
            dataSchema={},
            uiNodeType=UiNodeType.ACTION,
        )
        super().__init__(trigger)

    async def run(
        self,
        context: StepContext,
        app: AppDefinition,
        credentials: AppCredentials | None,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        if data is None:
            raise ValueError("Input data is required for triggers.")

        headers = data.get("headers", {})
        query_params = data.get("query_params", {})
        body = data.get("body", {})

        # Validate authentication
        auth_header = headers.get("authorization")
        if not auth_header:
            raise ValueError("Authorization header is missing")

        if credentials is not None and credentials.credentialsType == "basic":
            # Validate Basic auth
            import base64

            expected_auth = f"{credentials.username}:{credentials.password}"
            expected_header = (
                f"Basic {base64.b64encode(expected_auth.encode()).decode()}"
            )
            if auth_header != expected_header:
                raise ValueError("Invalid Basic authentication credentials")
        elif credentials is not None and credentials.credentialsType == "apikey":
            # Validate Bearer token using API key
            expected_header = f"Bearer {credentials.apiKey}"
            if auth_header != expected_header:
                raise ValueError("Invalid Bearer token")
        else:
            # No authentication required
            pass

        return {"headers": headers, "query_params": query_params, "body": body}
