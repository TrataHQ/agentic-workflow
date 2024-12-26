from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.session import get_session
from src.db.models.models import App, Connection
from src.crud.connection import connection
from src.crud.app import app
from src.models.connection import ConnectionCore, OAuthCredentials
from src.models.base import BaseResponse
from src.utils.auth import get_current_user, User
from src.services.oauth_service import OAuthResponse, OAuthService
from src.utils.helpers import is_token_expired

router = APIRouter(
    prefix="/v1/workflows/connections",
    tags=["connections"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Connection)
async def create_connection(
    *, 
    session: AsyncSession = Depends(get_session), 
    connection_in: ConnectionCore, 
    user: User = Depends(get_current_user)
):
    # Get the app from the database
    db_app = await app.get(session=session, id=connection_in.appId, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="Invalid app")
    
    assert db_app.auth.authType == connection_in.credentials.credentialsType, "Invalid credentials provided"

    connection_in = await get_token(connection_in, db_app)

    return await connection.create(session=session, obj_in=connection_in, user=user)

async def get_token(connection_in: ConnectionCore, db_app: App):
    if db_app.auth.authType == "oauth" and isinstance(connection_in.credentials, OAuthCredentials):
        oauth_service = OAuthService(
            token_url=db_app.auth.tokenUrl,
            client_id=db_app.auth.clientId,
            client_secret=db_app.auth.clientSecret,
            redirect_uri=db_app.auth.redirectUri
        )
        if connection_in.credentials.code:
            # Code grant flow
            oauth_response = await oauth_service.exchange_code_for_token(connection_in.credentials.code)
        else:
            # Implicit grant flow
            oauth_response = OAuthResponse(
                access_token=connection_in.credentials.accessToken,
                refresh_token=connection_in.credentials.refreshToken,
                expires_at=connection_in.credentials.expiresAt
            )
        # Update connection_in with access token and refresh token info
        connection_in.credentials.accessToken = oauth_response.access_token
        connection_in.credentials.refreshToken = oauth_response.refresh_token
        connection_in.credentials.expiresAt = oauth_response.expires_at
    return connection_in

@router.get("/", response_model=List[Connection])
async def read_connections(
    *, 
    session: AsyncSession = Depends(get_session), 
    skip: int = 0, 
    limit: int = 100, 
    user: User = Depends(get_current_user)
):
    return await connection.get_multi(session=session, skip=skip, limit=limit, user=user)

@router.get("/{connection_id}", response_model=Connection)
async def read_connection(
    *, 
    session: AsyncSession = Depends(get_session), 
    connection_id: str, 
    user: User = Depends(get_current_user)
):
    db_connection = await connection.get(session=session, id=connection_id, user=user)
    if not db_connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Refresh the OAuth token if the token is expired before returning the connection
    db_connection = await refresh_conn_if_required(session, user, db_connection)
    return db_connection

async def refresh_conn_if_required(session, user, db_connection):
    if db_connection.credentials.credentialsType == "oauth":
        if is_token_expired(db_connection.credentials.expiresAt):
            if not db_connection.credentials.refreshToken:
                raise HTTPException(status_code=404, detail="No refresh token available to refresh the connection")
            db_app = await app.get(session=session, id=db_connection.appId, user=user)
            if not db_app or db_app.auth.authType != "oauth":
                raise HTTPException(status_code=404, detail="Invalid app")
            oauth_service = OAuthService(
                token_url=db_app.auth.tokenUrl,
                client_id=db_app.auth.clientId,
                client_secret=db_app.auth.clientSecret,
                redirect_uri=db_app.auth.redirectUri
            )
            oauth_response = await oauth_service.refresh_token(db_connection.credentials.refreshToken)
            # Update the connection with new tokens
            db_connection = await connection.update(
                session=session,
                db_obj=db_connection,
                obj_in=ConnectionCore(
                    credentials=OAuthCredentials(
                        code=None,
                        accessToken=oauth_response.access_token,
                        refreshToken=oauth_response.refresh_token,
                        expiresAt=oauth_response.expires_at
                    )
                ),
                user=user
            )
            
    return db_connection

@router.put("/{connection_id}", response_model=Connection)
async def update_connection(
    *, 
    session: AsyncSession = Depends(get_session), 
    connection_id: str, 
    connection_in: ConnectionCore, 
    user: User = Depends(get_current_user)
):
    db_connection = await connection.get(session=session, id=connection_id, user=user)
    if not db_connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    db_app = await app.get(session=session, id=db_connection.appId, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="Invalid app")
    connection_in = await get_token(connection_in, db_app)
    return await connection.update(
        session=session, 
        db_obj=db_connection, 
        obj_in=connection_in, 
        user=user
    )

@router.delete("/{connection_id}", response_model=BaseResponse)
async def delete_connection(
    *, 
    session: AsyncSession = Depends(get_session), 
    connection_id: str, 
    user: User = Depends(get_current_user)
):
    db_connection = await connection.get(session=session, id=connection_id, user=user)
    if not db_connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    await connection.remove(session=session, id=connection_id, user=user)
    return BaseResponse(message="Connection deleted successfully", status="success") 
