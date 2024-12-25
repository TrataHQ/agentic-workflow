from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.session import get_session
from src.db.models.models import App
from src.crud.app import app
from src.crud.connection import connection
from src.models.app import AppCore
from src.models.base import BaseResponse
from src.models.connection import ConnectionCore
from src.utils.auth import get_current_user, User

router = APIRouter(
    prefix="/v1/workflows/apps",
    tags=["apps"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=App)
async def create_app(*, session: AsyncSession = Depends(get_session), app_in: AppCore, user: User = Depends(get_current_user)):
    return await app.create(session=session, obj_in=app_in, user=user)

@router.get("/", response_model=List[App])
async def read_apps(
    *, session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100, user: User = Depends(get_current_user)
):
    return await app.get_multi(session=session, skip=skip, limit=limit, user=user)

@router.get("/{app_id}", response_model=App)
async def read_app(*, session: AsyncSession = Depends(get_session), app_id: str, user: User = Depends(get_current_user)):
    db_app = await app.get(session=session, id=app_id, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    return db_app

@router.put("/{app_id}", response_model=App)
async def update_app(
    *, session: AsyncSession = Depends(get_session), app_id: str, app_in: AppCore, user: User = Depends(get_current_user)
):
    db_app = await app.get(session=session, id=app_id, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    return await app.update(session=session, db_obj=db_app, obj_in=app_in, user=user)

@router.delete("/{app_id}", response_model=BaseResponse)
async def delete_app(*, session: AsyncSession = Depends(get_session), app_id: str, user: User = Depends(get_current_user)):
    db_app = await app.get(session=session, id=app_id, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    await app.remove(session=session, id=app_id, user=user)
    return BaseResponse(message="App deleted successfully", status="success")

@router.get("/{app_id}/connections", response_model=List[ConnectionCore])
async def get_connections_by_app_id(
    *,
    session: AsyncSession = Depends(get_session),
    app_id: str,
    user: User = Depends(get_current_user)
):
    connections = await connection.get_by_app_id(session=session, app_id=app_id, user=user)
    return connections 
