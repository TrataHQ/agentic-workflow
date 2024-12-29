
from agentic_workflow.models.base import TenantModel
from agentic_workflow.utils.auth import User


SYSTEM_USER = User(
    id="system-user",
    email="support@trata.ai",
    role="system",
    tenantModel=TenantModel(orgId="system-org")
)