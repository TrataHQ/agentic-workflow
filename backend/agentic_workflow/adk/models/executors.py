from typing import Any, Dict, TYPE_CHECKING
from agentic_workflow.adk.models.app import AppActionEntity
from agentic_workflow.adk.models.connection import AppCredentials
from abc import abstractmethod
from agentic_workflow.adk.models.context import StepContext

if TYPE_CHECKING:
    from agentic_workflow.adk.models.app_definition import AppDefinition


class AppActionExecutor:
    def __init__(self, appAction: AppActionEntity):
        self.appAction = appAction

    @property
    def getAppActionEntity(self) -> AppActionEntity:
        return self.appAction

    @abstractmethod
    async def run(
        self,
        context: StepContext,
        app: "AppDefinition",
        credentials: AppCredentials | None,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute step logic"""
        pass
