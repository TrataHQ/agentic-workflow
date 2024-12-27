from typing import Any, Dict
from src.adk.models.app import Trigger, Action
from src.adk.models.connection import AppCredentials
from abc import abstractmethod
from src.adk.models.context import StepContext
from src.adk.models.app_definition import AppDefinition

class TriggerExecutor():
    def __init__(self, trigger: Trigger):
        self.trigger = trigger

    @abstractmethod
    async def run(self, context: StepContext, app: 'AppDefinition', credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trigger logic"""
        pass

class ActionExecutor():
    def __init__(self, action: Action):
        self.action = action

    @abstractmethod
    async def run(self, context: StepContext, app: 'AppDefinition', credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action logic"""
        pass 