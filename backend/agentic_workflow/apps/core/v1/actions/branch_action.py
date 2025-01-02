from typing import Any, Dict
from agentic_workflow.adk.models.executors import AppActionExecutor, StepContext
from agentic_workflow.adk.models.app import AppActionEntity, AppActionType, UiNodeType
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition

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
            uiSchema={},
            uiNodeType=UiNodeType.Condition
        )
        super().__init__(step)

    async def run(self, context: StepContext, app: AppDefinition, credentials: AppCredentials | None, data: Dict[str, Any]) -> Dict[str, Any]:
        # Simply return whatever data was passed in. The branch action is handled by next step resolver
        return data
