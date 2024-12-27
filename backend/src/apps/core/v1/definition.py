from typing import List
from src.adk.models.app_definition import AppDefinition
from src.adk.models.executors import TriggerExecutor, ActionExecutor
from src.adk.models.app import AppCore, NoAuth, BasicAuth, ApiKeyAuth
from src.adk.registry.app_registry import AppRegistry
from src.apps.core.v1.actions.branch_action import BranchAction
from src.apps.core.v1.triggers.webhook import WebhookTrigger

@AppRegistry.register
class CoreAppV1(AppDefinition):
    def get_definition(self) -> AppCore:
        return AppCore(
            name="Core",
            description="Core workflow control operations",
            version="1.0.0",
            logoUrl="https://path/to/core/logo.png",
            auth=[NoAuth(), BasicAuth(), ApiKeyAuth()],
            triggers=[a.trigger for a in self.triggers],
            actions=[a.action for a in self.actions]
        )

    @property
    def triggers(self) -> List[TriggerExecutor]:
        return [WebhookTrigger()]

    @property
    def actions(self) -> List[ActionExecutor]:
        return [
            BranchAction(),
        ]
