from typing import List
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.app import AppEntity, OAuth
from agentic_workflow.adk.models.executors import AppActionExecutor
from agentic_workflow.adk.registry.app_registry import AppRegistry
from agentic_workflow.apps.gmail.v1.actions.create_draft_action import CreateDraftAction
from agentic_workflow.apps.gmail.v1.actions.send_email_action import SendEmailAction

@AppRegistry.register
class GmailAppV1(AppDefinition):
    def get_definition(self) -> AppEntity:
        return AppEntity(
            name="Gmail",
            description="Gmail is a free, advertising-supported email service developed by Google. As of 2024, it provides 15 GB of storage per account and has integration with other Google services, including Google Docs, Google Calendar, and Google Drive.",
            version="1.0.0",
            logoUrl="https://firebasestorage.googleapis.com/v0/b/trata-prod.appspot.com/o/public-assets%2Flogos%2Fgoogle.svg?alt=media&token=0ce04cdd-94d7-4f88-8ecf-cab9a6ba83d4",
            auth=[OAuth(
                clientId="${GMAIL_CLIENT_ID}",
                clientSecret="${GMAIL_CLIENT_SECRET}",
                redirectUri="${GMAIL_REDIRECT_URI}",
                scopes=["gmail:send", "gmail:read"],
                authUrl="https://accounts.google.com/o/oauth2/auth",
                tokenUrl="https://oauth2.googleapis.com/token"
            )],
            actions=[a.appAction for a in self.appActions]
        )

    @property
    def appActions(self) -> List[AppActionExecutor]:
        return [
            SendEmailAction(),
            CreateDraftAction()
        ]
