from typing import List
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.executors import AppActionExecutor
from agentic_workflow.adk.models.app import AppEntity, NoAuth, BasicAuth, ApiKeyAuth
from agentic_workflow.adk.registry.app_registry import AppRegistry
from agentic_workflow.apps.core.v1.actions.branch_action import BranchAction
from agentic_workflow.apps.core.v1.actions.http_action import HttpAction
from agentic_workflow.apps.core.v1.triggers.webhook import WebhookTrigger

@AppRegistry.register
class CoreAppV1(AppDefinition):
    def get_definition(self) -> AppEntity:
        return AppEntity(
            name="Core",
            description="Basic workflow control operations like branching, webhook triggers, and more",
            version="1.0.0",
            logoUrl="https://firebasestorage.googleapis.com/v0/b/trata-prod.appspot.com/o/public-assets%2Flogos%2Fcore.svg?alt=media&token=f4b1cec3-f6b2-4c02-b194-a8cb3801b97b",
            auth=[NoAuth(), BasicAuth(), ApiKeyAuth()],
            actions=[a.appAction for a in self.appActions]
        )

    @property
    def appActions(self) -> List[AppActionExecutor]:
        return [WebhookTrigger(), BranchAction(), HttpAction()]
