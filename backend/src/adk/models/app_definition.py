from abc import ABC, abstractmethod
from typing import List
from src.adk.models.app import AppEntity
from src.adk.models.executors import AppActionExecutor

class AppDefinition(ABC):
    @abstractmethod
    def get_definition(self) -> AppEntity:
        """Return the app definition"""
        pass

    @property
    @abstractmethod
    def appActions(self) -> List[AppActionExecutor]:
        """Return list of steps with their executors"""
        pass
