from typing import Dict, List, Type
from agentic_workflow.adk.models.app_definition import AppDefinition
from agentic_workflow.adk.models.app import AppEntity
class AppRegistry:
    _instance = None
    _apps: Dict[str, Type[AppDefinition]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, app_class: Type[AppDefinition]):
        """Register an app definition"""
        app = app_class()
        definition = app.get_definition()
        key = f"{definition.name}-{definition.version}"
        cls._apps[key] = app_class
        return app_class

    @classmethod
    def get_all_apps(cls) -> List[AppEntity]:
        """Get all registered app definitions"""
        return list([app_class().get_definition() for app_class in cls._apps.values()])