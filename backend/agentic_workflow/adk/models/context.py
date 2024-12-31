from typing import Any, Dict

class StepContext:
    def __init__(self, step_id: str, workflow_id: str, input_data: Dict[str, Any]):
        self.step_id = step_id
        self.workflow_id = workflow_id
        self.input_data = input_data