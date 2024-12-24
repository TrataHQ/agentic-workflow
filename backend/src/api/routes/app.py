from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.db.session import get_session
from backend.src.db.models.models import App
from backend.src.crud.app import app
from backend.src.models.app import AppCore
from backend.src.models.base import BaseResponse
from backend.src.utils.auth import get_current_user, User

router = APIRouter("/v1/workflows/apps")

@router.post("/", response_model=App)
def create_app(*, session: AsyncSession = Depends(get_session), app_in: AppCore, user: User = Depends(get_current_user)):
    return app.create(session=session, obj_in=app_in)

@router.get("/", response_model=List[App])
def read_apps(
    *, session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100, user: User = Depends(get_current_user)
):
    return app.get_multi(session=session, skip=skip, limit=limit, tenantModel=user.tenantModel)

@router.get("/{app_id}", response_model=App)
def read_app(*, session: AsyncSession = Depends(get_session), app_id: int, user: User = Depends(get_current_user)):
    db_app = app.get(session=session, id=app_id, tenantModel=user.tenantModel)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    return db_app

@router.put("/{app_id}", response_model=App)
def update_app(
    *, session: AsyncSession = Depends(get_session), app_id: int, app_in: AppCore, user: User = Depends(get_current_user)
):
    db_app = app.get(session=session, id=app_id, tenantModel=user.tenantModel)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    return app.update(session=session, db_obj=db_app, obj_in=app_in, tenantModel=user.tenantModel)

@router.delete("/{app_id}", response_model=BaseResponse)
def delete_app(*, session: AsyncSession = Depends(get_session), app_id: int, user: User = Depends(get_current_user)):
    db_app = app.get(session=session, id=app_id, tenantModel=user.tenantModel)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    app.remove(session=session, id=app_id, tenantModel=user.tenantModel)
    return BaseResponse(message="App deleted successfully", status="success")
