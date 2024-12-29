from typing import Any, Dict, List
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.app import AppEntity, OAuth
from agentic_workflow.adk.models.executors import AppActionExecutor
from agentic_workflow.adk.registry.app_registry import AppRegistry
from agentic_workflow.apps.slack.v1.triggers.new_message_trigger import NewMessageTrigger
from agentic_workflow.apps.slack.v1.actions.send_message_action import SendMessageAction

@AppRegistry.register
class SlackAppV1(AppDefinition):
    def get_definition(self) -> AppEntity:
        return AppEntity(
            name="Slack",
            description="Slack integration for messaging and notifications",
            version="1.0.0",
            logoUrl="https://path/to/slack/logo.png",
            auth=[OAuth(
                clientId="${SLACK_CLIENT_ID}",
                clientSecret="${SLACK_CLIENT_SECRET}",
                redirectUri="${SLACK_REDIRECT_URI}",
                scopes=["chat:write", "channels:read"],
                authUrl="https://slack.com/oauth/v2/authorize",
                tokenUrl="https://slack.com/api/oauth.v2.access"
            )],
            actions=[a.appAction for a in self.appActions]
        )

    @property
    def appActions(self) -> List[AppActionExecutor]:
        return [
            NewMessageTrigger(),
            SendMessageAction()
        ]
