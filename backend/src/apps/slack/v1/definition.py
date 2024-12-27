from typing import Any, Dict, List
from src.adk.models.app_definition import AppDefinition
from src.adk.models.executors import TriggerExecutor, ActionExecutor
from src.adk.models.app import AppCore, OAuth
from src.adk.registry.app_registry import AppRegistry
from src.apps.slack.v1.triggers.new_message_trigger import NewMessageTrigger
from src.apps.slack.v1.actions.send_message_action import SendMessageAction

@AppRegistry.register
class SlackAppV1(AppDefinition):
    def get_definition(self) -> AppCore:
        return AppCore(
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
            triggers=[t.trigger for t in self.triggers],
            actions=[a.action for a in self.actions]
        )

    @property
    def triggers(self) -> List[TriggerExecutor]:
        return [
            NewMessageTrigger()
        ]

    @property
    def actions(self) -> List[ActionExecutor]:
        return [
            SendMessageAction()
        ]
