from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
import httpx
import base64
from email.mime.text import MIMEText

class CreateDraftAction(AppActionExecutor):
    def __init__(self):
        action = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="Create a draft email",
            description="Create a draft email",
            dataSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "title": "Email address to send the draft to."},
                    "subject": {"type": "string", "title": "Subject of the draft email."},
                    "body": {"type": "string", "title": "Body of the draft email."}
                },
                "required": ["to", "subject", "body"]
            },
            uiSchema={
                "to": {"ui:widget": "NextUITextField", "ui:placeholder": "Email address to send the draft to."},
                "subject": {"ui:widget": "NextUITextField", "ui:placeholder": "Subject of the draft email."},
                "body": {"ui:widget": "NextUITextareaField", "ui:placeholder": "Body of the draft email."}
            }
        )
        super().__init__(action)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials | None, data: Dict[str, Any]) -> Dict[str, Any]:

        if credentials is None:
            raise ValueError("Credentials are required to create a draft email")

        to = data["to"]
        subject = data["subject"]
        body = data["body"]
        sender = data["sender"]  # Sender email address

        # Create the email message
        message = MIMEText(body)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        # Encode the message in base64url
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        async with httpx.AsyncClient() as client:
            if credentials.credentialsType == "oauth":
                response = await client.post(
                    "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
                    headers={"Authorization": f"Bearer {credentials.accessToken}"},
                    json={
                        "message": {
                            "raw": raw_message
                        }
                    }
                )
            else:
                raise ValueError("Invalid credentials type")
            
            return response.json()
