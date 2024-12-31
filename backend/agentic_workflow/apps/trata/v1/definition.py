from typing import List
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.app import ApiKeyAuth, AppEntity
from agentic_workflow.adk.models.executors import AppActionExecutor
from agentic_workflow.adk.registry.app_registry import AppRegistry
from agentic_workflow.apps.trata.v1.actions.make_call_action import MakeCallAction
from agentic_workflow.apps.trata.v1.actions.get_contact_action import GetContactAction
from agentic_workflow.apps.trata.v1.actions.get_conversation_action import GetConversationAction
from agentic_workflow.apps.trata.v1.triggers.attend_call_trigger import AttendCallTrigger

@AppRegistry.register
class TrataAppV1(AppDefinition):
    def get_definition(self) -> AppEntity:
        return AppEntity(
            name="Trata AI",
            description="Human like conversation to answer service calls, automate follow-ups, customer feedback and offload level 1 support with end to end integrations.",
            version="1.0.0",
            logoUrl="https://framerusercontent.com/images/XGFSmep1J4VfnNQccQdebaiDBY.svg",
            auth=[ApiKeyAuth()],
            actions=[a.appAction for a in self.appActions]
        )

    @property
    def appActions(self) -> List[AppActionExecutor]:
        return [
            MakeCallAction(),
            GetContactAction(),
            GetConversationAction(),
            AttendCallTrigger()
        ]
