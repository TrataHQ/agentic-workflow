from typing import Dict, Any
from temporalio import workflow, activity
from temporalio.worker import Worker
from agentic_workflow.workflow import temporal_client
import logging
from datetime import timedelta
import importlib
import inspect
from typing import List
from pathlib import Path

with workflow.unsafe.imports_passed_through():
    from agentic_workflow.adk.models.workflow import WorkflowCore, WorkflowStep
    from agentic_workflow.adk.models.app import AppActionEntity
    from agentic_workflow.adk.models.context import StepContext
    from agentic_workflow.adk.models.app_definition import AppDefinition
    from agentic_workflow.adk.models.connection import ConnectionCore, AppCredentials
    from agentic_workflow.adk.models.app import AppActionType
    from agentic_workflow.adk.models.workflow import NextStepResolver, Condition
    from agentic_workflow.workflow.models.workflow_context import WorkflowContext
    from agentic_workflow.adk.models.app import AppEntity
    from agentic_workflow.db.session import get_session
    from agentic_workflow.crud.connection import connection
    from agentic_workflow.api.routes.connection import refresh_conn_if_required
    from agentic_workflow.utils.auth import User
    import jsonata
    from agentic_workflow.crud.workflow_execution import workflow_execution

@workflow.defn
class WorkflowOrchestrator:

    @workflow.run
    async def run(
        self,
        workflow_id: str,
        workflowCore: WorkflowCore,
        triggerPayload: Dict[str, Any],
        user: User,
    ):
        logging.info(f"Running workflow {workflow_id}")

        workflowContext: WorkflowContext = WorkflowContext(
            orgId=user.tenantModel.orgId,
            workflowId=workflow_id,
            stepInput={},
            stepResponse={},
            stepOrder=[],
        )
        workflowContext.stepInput[workflowCore.startStepId] = triggerPayload
        workflowSteps: Dict[str, WorkflowStep] = workflowCore.steps
        nextStepId: str | None = workflowCore.startStepId

        while nextStepId:
            workflowContext.stepOrder.append(nextStepId)
            workflowStep: WorkflowStep = workflowSteps[nextStepId]

            # prep and execute step
            workflowContext = await workflow.execute_activity(
                executeStep,
                args=[workflowContext, workflowStep, user],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=None,
            )

            # get next step id
            nextStepId = await workflow.execute_activity(
                nextStep,
                args=[workflowContext, workflowStep],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=None,
            )

        await workflow.execute_activity(
            updateWorkflowExecutionStatus, 
            args=[workflow_id, workflow.info().run_id, "COMPLETED", user],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=None,
        )
        
        return workflowContext
    


async def prepStepContext(workflowContext: WorkflowContext, workflowStep: WorkflowStep) -> StepContext:
    dataResolver: str | None = workflowStep.dataResolver
    workflowContextDict = workflowContext.model_dump()

    expression = jsonata.Jsonata(dataResolver)
    result: Dict[str, Any] | None = expression.evaluate(workflowContextDict)
    if not result:
        result = {}

    # Create step context
    return StepContext(
        step_id=workflowStep.stepId,
        workflow_id=workflowContext.workflowId,
        input_data=result,
    )


async def prepApp(workflowContext: WorkflowContext, workflowStep: WorkflowStep) -> AppDefinition | None:
    apps_dir = Path(__file__).parent.parent / "apps"

    for app_dir in apps_dir.iterdir():
        if not app_dir.is_dir():
            continue

        for version_dir in app_dir.iterdir():
            if not version_dir.is_dir():
                continue

            # Convert path to module path
            module_path = str(version_dir / "definition.py")
            if not Path(module_path).exists():
                continue

            # Convert file path to module path
            relative_path = version_dir.relative_to(Path(__file__).parent.parent)
            module_name = ".".join(relative_path.parts)
            try:
                appModule = importlib.import_module(f"agentic_workflow.{module_name}.definition")
                appClass = next(
                    cls
                    for _, cls in inspect.getmembers(appModule, inspect.isclass)
                    if issubclass(cls, AppDefinition) and cls is not AppDefinition
                )
                appInstance = appClass()
                appEntity: AppEntity = appInstance.get_definition()

                if appEntity.name == workflowStep.appName and appEntity.version == workflowStep.appVersion:
                    return appInstance
            except Exception as e:
                logging.error(f"Error importing {module_name}: {e}")

    return None


async def prepCredentials(
    workflowContext: WorkflowContext, workflowStep: WorkflowStep, user: User
) -> AppCredentials | None:
    connectionId = workflowStep.appConnectionId
    appId = workflowStep.appId
    version = workflowStep.appVersion
    orgId = workflowContext.orgId

    credentials = None
    async for session in get_session():
        db_connection = await connection.get(session=session, pk=connectionId, user=user)
        if db_connection:
            db_connection = await refresh_conn_if_required(session, user, db_connection)
            if db_connection:
                credentials = db_connection.credentials

    return credentials


@activity.defn
async def executeStep(workflowContext: WorkflowContext, workflowStep: WorkflowStep, user: User) -> WorkflowContext:
    logging.info("Executing step")

    # Prep step
    app = await prepApp(workflowContext, workflowStep)
    if not app:
        raise Exception(f"App {workflowStep.appName} not found")
    credentials = await prepCredentials(workflowContext, workflowStep, user)
    stepContext = await prepStepContext(workflowContext, workflowStep)

    # Execute step
    stepPayload: AppActionEntity = workflowStep.stepPayload
    actionType: AppActionType = stepPayload.actionType
    actionName: str = stepPayload.name

    result: Dict[str, Any] = {}
    actions = app.appActions
    action = next((a for a in actions if a.getAppActionEntity.name == actionName), None)
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

@activity.defn
async def updateWorkflowExecutionStatus(workflow_id: str, workflowRunId: str, status: str, user: User) -> None:
    async for session in get_session():
        await workflow_execution.update_workflow_execution_status_by_temporal_run_id(session=session, workflow_id=workflow_id, temporal_run_id=workflowRunId, status=status, user=user)

async def init_workflow_orchestrator(workflow_id: str, workflowCore: WorkflowCore, triggerPayload: Dict[str, Any], user: User) -> str | None:
    client = await temporal_client.get_client()
    result = await client.start_workflow(
        WorkflowOrchestrator.run,
        args=[workflow_id, workflowCore, triggerPayload, user],
        id=workflow_id,
        task_queue="workflow-orchestrator",
    )
    description = await result.describe()
    logging.info(f"Workflow description: {description.run_id}")
    return description.run_id


async def init_workflow_orchestrator_worker() -> None:
    logging.info("Obtaining client")
    client = await temporal_client.get_client()
    logging.info("Creating worker")
    worker = Worker(
        client,
        task_queue="workflow-orchestrator",
        workflows=[WorkflowOrchestrator],
        activities=[executeStep, nextStep, updateWorkflowExecutionStatus],
    )
    logging.info("Running worker")
    await worker.run()
    logging.info("Worker running")
