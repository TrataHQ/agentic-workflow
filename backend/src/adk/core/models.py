from abc import ABC, abstractmethod
from typing import Any, Dict, List
from src.adk.models.app import AppCore, Trigger, Action
from src.adk.models.connection import AppCredentials
from fastapi import Request

class StepContext:
    def __init__(self, step_id: str, workflow_id: str, input_data: Dict[str, Any], request: Request | None = None):
        self.step_id = step_id
        self.workflow_id = workflow_id
        self.input_data = input_data
        self.request = request

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

class AppDefinition(ABC):
    @abstractmethod
    def get_definition(self) -> AppCore:
        """Return the app definition"""
        pass

    @property
    @abstractmethod
    def triggers(self) -> List[TriggerExecutor]:
        """Return list of triggers with their executors"""
        pass

    @property
    @abstractmethod
    def actions(self) -> List[ActionExecutor]:
        """Return list of actions with their executors"""
        pass 
