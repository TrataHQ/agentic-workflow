from temporalio.client import Client
import os


async def get_client():
    TEMPORAL_SERVICE = os.getenv("TEMPORAL_SERVICE", None)
    TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", None)
    TEMPORAL_API_KEY = os.getenv("TEMPORAL_API_KEY", None)

    if (
        TEMPORAL_SERVICE is None
        or TEMPORAL_NAMESPACE is None
        or TEMPORAL_API_KEY is None
    ):
        raise ValueError("Invalid Temporal configuration")

    client = await Client.connect(
        TEMPORAL_SERVICE,
        namespace=TEMPORAL_NAMESPACE,
        rpc_metadata={"temporal-namespace": TEMPORAL_NAMESPACE},
        api_key=TEMPORAL_API_KEY,
        tls=True,
    )
    return client
