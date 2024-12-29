from typing import Dict, Any
from temporalio import workflow, activity
from temporalio.worker import Worker
from agentic_workflow.workflow import temporal_client
import logging
from datetime import timedelta
import re
import importlib
import inspect
from typing import List
with workflow.unsafe.imports_passed_through():
    from agentic_workflow.adk.models.workflow import WorkflowCore, WorkflowStep
    from agentic_workflow.workflow.models.workflow_context import WorkflowActionExecutionContext
    from agentic_workflow.adk.models.app import AppActionEntity
    from agentic_workflow.adk.models.context import StepContext
    from agentic_workflow.adk.models.app_definition import AppDefinition
    from agentic_workflow.adk.models.connection import ConnectionCore, AppCredentials
    from agentic_workflow.adk.models.app import AppActionType
    from agentic_workflow.adk.models.workflow import NextStepResolver, Condition
    import jsonata

@workflow.defn
class WorkflowOrchestrator:
    
    @workflow.run
    async def run(self, orgId: str, workflow_id: str, dsl: dict, payload: Dict[str, Any]):
        logging.info(f"Running workflow {workflow_id}")

        dsl = {
            "name": "Sheik",
            "description": "Sheik",
            "version": "1.0.0",
            "steps": {
                "step1": {
                    "stepId": "step1",
                    "appConnectionId": "slack_con",
                    "appId": "slack", # TODO: We will get it from proer table (important player to resolve app path)
                    "appVersion": "v1", # TODO: We will get it from proer table (important player to resolve app path)
                    "stepPayload": {
                        "actionType": "action",
                        "name": "SendMessageAction", # TODO: We will get it from proer table (important player to get the execution method)
                        "description": "Send a message to a channel",
                        "dataSchema": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "message": {"type": "string"}
                            }
                        },
                        "uiSchema": {
                            "channel": {"ui:widget": "select"}
                        }
                    },
                    "dataResolver": {
                        "channel": "Sales Team Channel",
                        "message": "hi {triggerPayload.channel} this is a message {triggerPayload.name}"
                    },
                    "nextStepResolver": {
                        "conditions": [
                            {
                                "when": "triggerPayload.price > 100",
                                "stepId": "step3"
                            },
                            {
                                "when": "triggerPayload.price < 100",
                                "stepId": "step4"
                            },
                            {
                                "when": "triggerPayload.price = 100",
                                "stepId": "step5"
                            },
                            {
                                "when": "true",
                                "stepId": "step6"
                            }
                        ]
                        # "nextStepId": "step2"
                    }
                }
            },
            "startStepId": "step1"
        }

        payload = {
            "channel": "Sales Team Channel",
            "name": "Sheik",
            "price": 100
        }

        

        

        workflowCore = WorkflowCore(**dsl)



        workflowContext: Dict[str, Any] = {
            "workflowId": workflow_id,
            "triggerPayload": payload,
            "stepPayload": {},
            "stepResponse": {}
        }

        workflowSteps: Dict[str, WorkflowStep] = workflowCore.steps
        stepId: str | None = workflowCore.startStepId

        while stepId:
            workflowStep: WorkflowStep = workflowSteps[stepId]
            
            # prep and execute step
            await workflow.execute_activity(
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

async def prepStep(workflowContext: Dict[str, Any], workflowStep: WorkflowStep) -> WorkflowActionExecutionContext:
    logging.info("Preparing step")
    stepPayload: AppActionEntity = workflowStep.stepPayload
    dataSchema: Dict = stepPayload.dataSchema
    dataResolver: Dict = workflowStep.dataResolver

    logging.info(f"Data resolver before: {dataResolver}")
    # Resolve data
    for key, value in dataResolver.items():
        placeholders = re.findall(r"\{(.*?)\}", value)
        for placeholder in placeholders:
            expression = jsonata.Jsonata(placeholder)
            result = expression.evaluate(workflowContext)
            value = value.replace(f"{{{placeholder}}}", str(result))
        dataResolver[key] = value

    logging.info(f"Data resolver after: {dataResolver}")

    # Create step context
    stepContext = StepContext(
        step_id=workflowStep.stepId,
        workflow_id=workflowContext["workflowId"],
        input_data=dataResolver
    )

    # Create app instance
    appPath = f"agentic_workflow.apps.{workflowStep.appId}.{workflowStep.appVersion}.definition" # TODO: We will get it from proer table
    appModule = importlib.import_module(appPath)
    appClass = next(
        cls for _, cls in inspect.getmembers(appModule, inspect.isclass)
        if issubclass(cls, AppDefinition) and cls is not AppDefinition
    )
    appInstance = appClass()

    # TODO: Get credentials from corresponding table
    # Get credentials 
    credentials: AppCredentials = None

    return WorkflowActionExecutionContext(
        stepContext=stepContext,
        app=appInstance,
        credentials=credentials,
        data=workflowContext
    )

@activity.defn
async def executeStep(workflowContext: Dict[str, Any], workflowStep: WorkflowStep):
    logging.info("Executing step")

    # Prep step
    workflowActionExecutionContext = await prepStep(workflowContext, workflowStep)

    # Execute step
    stepPayload: AppActionEntity = workflowStep.stepPayload
    actionType: AppActionType = stepPayload.actionType
    executorName: str = stepPayload.name # TODO: Verify if this is the correct way to get the execution method (important player to get the execution method)
    app: AppDefinition = workflowActionExecutionContext.app
    credentials: AppCredentials | None = workflowActionExecutionContext.credentials
    stepContext: StepContext = workflowActionExecutionContext.stepContext
    data: Dict[str, Any] = workflowActionExecutionContext.data

    actions = app.appActions
    action = next((a for a in actions if a.__class__.__name__ == executorName), None)
    result = None
    if action:
        logging.info(f"Action: {action}")
        result = await action.run(stepContext, app, credentials, data)

    # Update action payload and response to workflow context
    workflowContext["stepResponse"][workflowStep.stepId] = result
    workflowContext["stepPayload"][workflowStep.stepId] = stepContext.input_data

    
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
        nextStepResolverDict = nextStepResolver.to_dict()

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




async def init_workflow_orchestrator(orgId: str, workflow_id: str) -> None:
    client = await temporal_client.get_client()
    workflow_id = f"workflow-orchestrator-{workflow_id}"
    result = await client.start_workflow(
        WorkflowOrchestrator.run,
        args=[orgId, workflow_id, {}, {}],
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
