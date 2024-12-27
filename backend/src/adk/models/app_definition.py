from abc import ABC, abstractmethod
from typing import List
from src.adk.models.app import AppCore
from src.adk.models.executors import TriggerExecutor, ActionExecutor

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