from agentic_workflow.db.models import Workflow
from agentic_workflow.crud.base import CRUDBase
from agentic_workflow.adk.models.workflow import WorkflowCore

class CRUDWorkflow(CRUDBase[Workflow, WorkflowCore, WorkflowCore]):
    pass

workflow = CRUDWorkflow(Workflow, primary_keys=["id"])
