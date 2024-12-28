from typing import Any, Dict
from src.adk.models.executors import AppActionExecutor, StepContext
from src.adk.models.app import AppActionEntity, AppActionType
from src.adk.models.connection import AppCredentials
from src.adk.models.app_definition import AppDefinition

class BranchAction(AppActionExecutor):
    def __init__(self):
        step = AppActionEntity(
            actionType=AppActionType.ACTION,
            name="branch",
            description="Branch point in workflow - passes through input data",
            dataSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Data to pass through"
                    }
                }
            },
            uiSchema={}
        )
        super().__init__(step)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials, data: Dict[str, Any]) -> Dict[str, Any]:
        # Simply return whatever data was passed in
        return data
