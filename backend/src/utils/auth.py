from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.models.base import TenantModel
from pydantic import BaseModel

class User(BaseModel):
    """Protocol defining the required user attributes"""
    id: str
    email: str
    role: str | None
    tenantModel: TenantModel

class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    async def get_user_from_token(
        self,
        credentials: HTTPAuthorizationCredentials,
        request: Request
    ) -> Optional[User]:
        """
        Authenticate and return a user from a token.
        
        Args:
            credentials: The authorization credentials
            request: The incoming request object
            
        Returns:
            Optional[User]: The authenticated user or None if authentication fails
            
        Raises:
            HTTPException: If authentication fails
        """
        pass

    @abstractmethod
    async def authorize(self, user: User, request: Request) -> bool:
        """
        Check if a user has permission to perform the requested action.
        
        Args:
            user: The authenticated user
            request: The incoming request
            
        Returns:
            bool: True if authorized, False otherwise
        """
        pass

bearer_scheme = HTTPBearer(auto_error=False)

async def get_auth_provider(request: Request) -> AuthProvider:
    """FastAPI dependency to get the configured auth provider"""
    return request.app.state.auth_provider

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    request: Request = None,
    auth_provider: AuthProvider = Depends(get_auth_provider)
) -> User:
    """
    Dependency that handles authentication and authorization.
    
    Usage:
        @router.post("/")
        async def create_item(user: User = Depends(get_current_user)):
            # user object is available here
    """

    try:
        user = await auth_provider.get_user_from_token(credentials, request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Check authorization
        is_authorized = await auth_provider.authorize(user, request)
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this operation"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

