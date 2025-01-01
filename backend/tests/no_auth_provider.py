import pytest
from agentic_workflow.utils.auth import AuthProvider, User
from agentic_workflow.models.base import TenantModel
from uuid import uuid4

@pytest.fixture(scope="session")
def session_org_id():
    """Generate a unique org ID for the entire test session"""
    return f"test_tenant_{uuid4()}"
