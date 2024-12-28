from typing import List
from src.adk.models.app_definition import AppDefinition
from src.adk.models.executors import AppActionExecutor
from src.adk.models.app import AppEntity, NoAuth, BasicAuth, ApiKeyAuth
from src.adk.registry.app_registry import AppRegistry
from src.apps.core.v1.actions.branch_action import BranchAction
from src.apps.core.v1.triggers.webhook import WebhookTrigger

@AppRegistry.register
class CoreAppV1(AppDefinition):
    def get_definition(self) -> AppEntity:
        return AppEntity(
            name="Core",
            description="Core workflow control operations",
            version="1.0.0",
            logoUrl="https://path/to/core/logo.png",
            auth=[NoAuth(), BasicAuth(), ApiKeyAuth()],
            actions=[a.appAction for a in self.appActions]
        )

    @property
    def appActions(self) -> List[AppActionExecutor]:
        return [WebhookTrigger(), BranchAction()]