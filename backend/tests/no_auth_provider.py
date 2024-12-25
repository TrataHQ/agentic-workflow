import pytest
from src.utils.auth import AuthProvider, User
from src.models.base import TenantModel
from uuid import uuid4

@pytest.fixture(scope="session")
def session_org_id():
    """Generate a unique org ID for the entire test session"""
    return f"test_tenant_{uuid4()}"

class NoAuthProvider(AuthProvider):
    def __init__(self, org_id: str = "tenant1"):
        self.org_id = org_id

    async def get_user_from_token(self, credentials, request):
        mock_user = User(
            id="1",
            email="test@test.com",
            role="admin",
            tenantModel=TenantModel(orgId=self.org_id)
        )
        return mock_user 

    async def authorize(self, user, request):
        return True
