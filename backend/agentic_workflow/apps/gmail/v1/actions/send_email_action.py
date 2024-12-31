from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx
import base64
from email.mime.text import MIMEText

class SendEmailAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Send an email",
            description="Send an email to a user",
            dataSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "title": "Email Address"},
                    "subject": {"type": "string", "title": "Subject"},
                    "body": {"type": "string", "title": "Body"}
                },
                "required": ["to", "subject", "body"]
            },
            uiSchema={
                "to": {"ui:widget": "NextUITextField", "ui:placeholder": "Email Address"},
                "subject": {"ui:widget": "NextUITextField", "ui:placeholder": "Subject"},
                "body": {"ui:widget": "NextUITextareaField", "ui:placeholder": "Body"}
            }
        )
        super().__init__(action)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        to = data["to"]
        subject = data["subject"]
        body: str = data["body"]
        sender = data["sender"]  # Add the sender's email address

        message = MIMEText(body)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        # Encode the message in base64url
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        async with httpx.AsyncClient() as client:
            if credentials.credentialsType == "oauth":
                response = await client.post(
                    "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                    headers={"Authorization": f"Bearer {credentials.accessToken}"},
                    json={"raw": raw_message}
                )
            else:
                raise ValueError("Invalid credentials type")
        return response.json()
