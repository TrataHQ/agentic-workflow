from typing import Any, Dict, List
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.app import AppEntity, OAuth
from agentic_workflow.adk.models.executors import AppActionExecutor
from agentic_workflow.adk.registry.app_registry import AppRegistry
from agentic_workflow.apps.slack.v1.actions.send_dm_action import (
    SendDirectMessageAction,
)
from agentic_workflow.apps.slack.v1.actions.send_channel_message_action import (
    SendChannelMessageAction,
)


@AppRegistry.register
class SlackAppV1(AppDefinition):
    def get_definition(self) -> AppEntity:
        return AppEntity(
            name="Slack",
            description="Slack brings team communication and collaboration into one place so you can get more work done, whether you belong to a large enterprise or a small business",
            version="1.0.0",
            logoUrl="https://firebasestorage.googleapis.com/v0/b/trata-prod.appspot.com/o/public-assets%2Flogos%2Fslack_icon.svg?alt=media&token=738cb7d7-2ec8-4b38-819c-b2e4d0b0e9f6",
            auth=[
                OAuth(
                    clientId="${SLACK_CLIENT_ID}",
                    clientSecret="${SLACK_CLIENT_SECRET}",
                    redirectUri="${SLACK_REDIRECT_URI}",
                    scopes=[
                        "chat:write",
                        "channels:read",
                        "groups:read",
                        "channels:history",
                        "groups:history",
                        "app_mentions:read",
                    ],
                    authUrl="https://slack.com/oauth/v2/authorize",
                    tokenUrl="https://slack.com/api/oauth.v2.access",
                )
            ],
            actions=[a.appAction for a in self.appActions],
        )

    @property
    def appActions(self) -> List[AppActionExecutor]:
        return [SendChannelMessageAction(), SendDirectMessageAction()]
