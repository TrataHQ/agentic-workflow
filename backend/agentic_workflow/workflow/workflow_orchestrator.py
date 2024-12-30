from typing import Dict, Any
from temporalio import workflow, activity
from temporalio.worker import Worker
from agentic_workflow.workflow import temporal_client
import logging
from datetime import timedelta
import importlib
import inspect
from typing import List

with workflow.unsafe.imports_passed_through():
    from agentic_workflow.adk.models.workflow import WorkflowCore, WorkflowStep
    from agentic_workflow.adk.models.app import AppActionEntity
    from agentic_workflow.adk.models.context import StepContext
    from agentic_workflow.adk.models.app_definition import AppDefinition
    from agentic_workflow.adk.models.connection import ConnectionCore, AppCredentials
    from agentic_workflow.adk.models.app import AppActionType
    from agentic_workflow.adk.models.workflow import NextStepResolver, Condition
    from agentic_workflow.workflow.models.workflow_context import WorkflowContext
    import jsonata

@workflow.defn
class WorkflowOrchestrator:
    
    @workflow.run
    async def run(self, orgId: str, workflow_id: str, workflowCore: WorkflowCore, triggerPayload: Dict[str, Any]):
        logging.info(f"Running workflow {workflow_id}")
        
        workflowContext: WorkflowContext = WorkflowContext(
            workflowId=workflow_id,
            triggerPayload=triggerPayload,
            stepInput={},
            stepResponse={}
        )

        workflowSteps: Dict[str, WorkflowStep] = workflowCore.steps
        stepId: str | None = workflowCore.startStepId

        while stepId:
            workflowStep: WorkflowStep = workflowSteps[stepId]
            
            # prep and execute step
            workflowContext = await workflow.execute_activity(
                executeStep,
                args=[workflowContext, workflowStep],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=None
            )

            # get next step id
            stepId = await workflow.execute_activity(
                nextStep,
                args=[workflowContext, workflowStep],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=None
            )

            stepId = None

async def prepStepContext(workflowContext: WorkflowContext, workflowStep: WorkflowStep) -> StepContext:
    dataResolver: str|None = workflowStep.dataResolver
    workflowContextDict = workflowContext.model_dump()

    expression = jsonata.Jsonata(dataResolver)
    result: Dict[str, Any] | None = expression.evaluate(workflowContextDict)
    if not result:
        result = {}

    # Create step context
    return StepContext(
        step_id=workflowStep.stepId,
        workflow_id=workflowContext.workflowId,
        input_data=result
    )

async def prepApp(workflowContext: WorkflowContext, workflowStep: WorkflowStep) -> AppDefinition:
    appPath = f"agentic_workflow.apps.{workflowStep.appId}.{workflowStep.appVersion}.definition" # TODO: We will get it from proer table
    appModule = importlib.import_module(appPath)
    appClass = next(
        cls for _, cls in inspect.getmembers(appModule, inspect.isclass)
        if issubclass(cls, AppDefinition) and cls is not AppDefinition
    )
    return appClass()

async def prepCredentials(workflowContext: WorkflowContext, workflowStep: WorkflowStep) -> AppCredentials:
    # TODO: Get credentials from corresponding table
    credentials: AppCredentials = None
    return credentials

@activity.defn
async def executeStep(workflowContext: WorkflowContext, workflowStep: WorkflowStep) -> WorkflowContext:
    logging.info("Executing step")

    # Prep step
    stepContext = await prepStepContext(workflowContext, workflowStep)
    app = await prepApp(workflowContext, workflowStep)
    credentials = await prepCredentials(workflowContext, workflowStep)

    # Execute step
    stepPayload: AppActionEntity = workflowStep.stepPayload
    actionType: AppActionType = stepPayload.actionType
    executorName: str = stepPayload.name # TODO: Verify if this is the correct way to get the execution method (important player to get the execution method)

    actions = app.appActions
    action = next((a for a in actions if a.__class__.__name__ == executorName), None)
    result = None
    if action:
        logging.info(f"Action: {action}")
        result = await action.run(stepContext, app, credentials, workflowContext.model_dump())

    # Update action payload and response to workflow context
    workflowContext.stepResponse[workflowStep.stepId] = result
    workflowContext.stepInput[workflowStep.stepId] = stepContext.input_data

    return workflowContext
    
    
@activity.defn
async def nextStep(workflowContext: Dict[str, Any], workflowStep: WorkflowStep) -> str | None:
    logging.info("Next step")
    nextStepResolver: NextStepResolver = workflowStep.nextStepResolver
    conditions: List[Condition] | None = nextStepResolver.conditions
    nextStepId: str | None = nextStepResolver.nextStepId

    if not conditions and not nextStepId:
        return None
    
    if nextStepId:
        return nextStepId

    if conditions:
        nextStepResolverDict = nextStepResolver.model_dump()

        expression = jsonata.Jsonata("conditions.when")
        whenConditions = expression.evaluate(nextStepResolverDict)
        if whenConditions:
            conditionIndex = 0
            for condition in whenConditions:
                expression = jsonata.Jsonata(condition)
                result = expression.evaluate(workflowContext)
                if result and result == True:
                    expression = jsonata.Jsonata(f"conditions[{conditionIndex}].stepId")
                    stepId = expression.evaluate(nextStepResolverDict)
                    return stepId
                conditionIndex += 1

    return None


async def init_workflow_orchestrator(orgId: str, workflow_id: str, workflowCore: WorkflowCore, triggerPayload: Dict[str, Any]) -> None:
    client = await temporal_client.get_client()
    workflow_id = f"workflow-orchestrator-{workflow_id}"
    result = await client.start_workflow(
        WorkflowOrchestrator.run,
        args=[orgId, workflow_id, workflowCore, triggerPayload],
        id=workflow_id,
        task_queue="workflow-orchestrator"
    )

async def init_workflow_orchestrator_worker() -> None:
    logging.info("Obtaining client")
    client = await temporal_client.get_client()
    logging.info("Creating worker")
    worker = Worker(
        client,
        task_queue="workflow-orchestrator",
        workflows=[WorkflowOrchestrator],
        activities=[
            executeStep,
            nextStep
        ]
        
    )
    logging.info("Running worker")
    await worker.run()
    logging.info("Worker running")
