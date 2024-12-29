from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.db.session import get_session
from agentic_workflow.db.models import App, AppAction
from agentic_workflow.crud.app import app as app_crud
from agentic_workflow.crud.app_action import app_action as app_action_crud
from agentic_workflow.crud.connection import connection as connection_crud
from agentic_workflow.adk.models.app import AppActionCore, AppCore, AppEntity
from agentic_workflow.models.base import BaseResponse
from agentic_workflow.adk.models.connection import ConnectionCore
from agentic_workflow.utils.auth import get_current_user, User

#### App response model
class AppResponse(SQLModel):
    app: App
    actions: List[AppAction]

router = APIRouter(
    prefix="/v1/workflows/apps",
    tags=["apps"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=AppResponse)
async def create_app(*, session: AsyncSession = Depends(get_session), app_in: AppEntity, user: User = Depends(get_current_user)) -> AppResponse:
    app_entity = AppEntity(**app_in.model_dump())
    app_obj = await app_crud.create_no_commit(session=session, obj_in=app_entity, user=user)
    # Create actions and triggers
    for action in app_in.actions:
        action_entity = AppActionCore(**action.model_dump(), appId=app_obj.id, appVersion=app_obj.version)
        await app_action_crud.create_no_commit(session=session, obj_in=action_entity, user=user)
    await session.commit()
    await session.refresh(app_obj)
    actions = await app_action_crud.get_by_app_id(session=session, app_id=app_obj.id, app_version=app_obj.version, user=user)
    return AppResponse(app=app_obj, actions=actions)

@router.get("/", response_model=List[AppResponse])
async def read_apps(
    *, session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100, user: User = Depends(get_current_user)
) -> List[AppResponse]:
    apps = await app_crud.get_multi(session=session, skip=skip, limit=limit, user=user)
    app_responses = []
    for app in apps:
        actions = await app_action_crud.get_by_app_id(session=session, app_id=app.id, app_version=app.version, user=user)
        app_responses.append(AppResponse(app=app, actions=actions))
    return app_responses

@router.get("/{app_id}", response_model=AppResponse)
async def read_app(*, session: AsyncSession = Depends(get_session), app_id: str, version: str | None = None, user: User = Depends(get_current_user)):
    if version:
        db_app = await app_crud.get(session=session, pk=(app_id, version), user=user)
    else:
        db_app = await app_crud.get(session=session, pk=app_id, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    actions = await app_action_crud.get_by_app_id(session=session, app_id=db_app.id, app_version=db_app.version, user=user)
    return AppResponse(app=db_app, actions=actions)

@router.put("/{app_id}", response_model=AppResponse)
async def update_app(
    *, session: AsyncSession = Depends(get_session), app_id: str, version: str | None = None, app_in: AppEntity, user: User = Depends(get_current_user)
) -> AppResponse:
    if version:
        db_app = await app_crud.get(session=session, pk=(app_id, version), user=user)
    else:
        db_app = await app_crud.get(session=session, pk=app_id, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    # Create new version of the app
    updated_app = await app_crud.create_no_commit(session=session, obj_in=app_in, user=user)
    actions = app_in.actions
    for action in actions:
        action_entity = AppActionCore(**action.model_dump(), appId=updated_app.id, appVersion=updated_app.version)
        await app_action_crud.create_no_commit(session=session, obj_in=action_entity, user=user)
    await session.commit()
    await session.refresh(updated_app)
    db_actions = await app_action_crud.get_by_app_id(session=session, app_id=updated_app.id, app_version=updated_app.version, user=user)
    return AppResponse(app=updated_app, actions=db_actions)

@router.delete("/{app_id}", response_model=BaseResponse)
async def delete_app(*, session: AsyncSession = Depends(get_session), app_id: str, version: str | None = None, user: User = Depends(get_current_user)):
    if version:
        db_app = await app_crud.get(session=session, pk=(app_id, version), user=user)
    else:
        db_app = await app_crud.get(session=session, pk=app_id, user=user)
    if not db_app:
        raise HTTPException(status_code=404, detail="App not found")
    await app_action_crud.remove_by_app_id_no_commit(session=session, app_id=db_app.id, app_version=db_app.version, user=user)
    await app_crud.remove_no_commit(session=session, pk=(db_app.id, db_app.version), user=user)
    await session.commit()
    return BaseResponse(message="App deleted successfully", status="success")

@router.get("/{app_id}/versions/{version}/connections", response_model=List[ConnectionCore])
async def get_connections_by_app_id(
    *,
    session: AsyncSession = Depends(get_session),
    app_id: str,
    version: str,
    user: User = Depends(get_current_user)
):
    connections = await connection_crud.get_by_app_id(session=session, app_id=app_id, version=version, user=user)
    return connections 
