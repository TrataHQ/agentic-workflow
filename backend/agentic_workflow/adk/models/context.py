from typing import Any, Dict
from fastapi import Request

class StepContext:
    def __init__(self, step_id: str, workflow_id: str, input_data: Dict[str, Any], request: Request | None = None):
        self.step_id = step_id
        self.workflow_id = workflow_id
        self.input_data = input_data
        self.request = request 