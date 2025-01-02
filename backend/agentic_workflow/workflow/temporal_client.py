from temporalio.client import Client
import os
import logging
import temporalio.api.enums.v1
async def get_client():
    TEMPORAL_SERVICE = os.getenv("TEMPORAL_SERVICE", None)
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", None)
    TEMPORAL_API_KEY = os.getenv("TEMPORAL_API_KEY", None)

    if TEMPORAL_SERVICE is None or TEMPORAL_NAMESPACE is None or TEMPORAL_API_KEY is None:
        raise ValueError("Invalid Temporal configuration")

    client = await Client.connect(
        TEMPORAL_SERVICE,
        namespace=TEMPORAL_NAMESPACE,
        rpc_metadata={"temporal-namespace": TEMPORAL_NAMESPACE},
        api_key=TEMPORAL_API_KEY,
        tls=True,
    )
    return client


async def get_workflow_run_history(workflow_id, run_id):
    temporal_client = await get_client()
    workflow_handle = temporal_client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)
    result = await workflow_handle.result()
    return result