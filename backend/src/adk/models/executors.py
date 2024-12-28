from typing import Any, Dict, TYPE_CHECKING
from src.adk.models.app import AppActionEntity
from src.adk.models.connection import AppCredentials
from abc import abstractmethod
from src.adk.models.context import StepContext

if TYPE_CHECKING:
    from src.adk.models.app_definition import AppDefinition

class AppActionExecutor():
    def __init__(self, appAction: AppActionEntity):
        self.appAction = appAction

    @abstractmethod
    async def run(self, context: StepContext, app: 'AppDefinition', credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute step logic"""
        pass
