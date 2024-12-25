from src.utils.auth import AuthProvider, User
from src.models.base import TenantModel

class NoAuthProvider(AuthProvider):
    async def get_user_from_token(self, credentials, request):
        mock_user = User(
            id="1",
            email="test@test.com",
            role="admin",
            tenantModel=TenantModel(orgId="tenant1")
        )
        return mock_user 

    async def authorize(self, user, request):
        return True
