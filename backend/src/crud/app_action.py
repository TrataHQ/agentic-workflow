from typing import List
from sqlmodel import select
from src.constants import SYSTEM_USER
from src.utils.auth import User
from .base import CRUDBase
from src.adk.models.app import AppActionCore
from src.db.models import AppAction
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import col

class CRUDAppAction(CRUDBase[AppAction, AppActionCore, AppActionCore]):
    async def get_by_app_id(self, session: AsyncSession, app_id: str, app_version: str, user: User) -> List[AppAction]:
        statement = select(self.model).where(
            col(self.model.orgId).in_([user.tenantModel.orgId, SYSTEM_USER.tenantModel.orgId]),
            self.model.appId == app_id,
            self.model.appVersion == app_version
        )
        result = await session.exec(statement)
        return list(result.all())

    async def remove_by_app_id_no_commit(self, session: AsyncSession, app_id: str, app_version: str, user: User) -> None:
        actions = await self.get_by_app_id(session=session, app_id=app_id, app_version=app_version, user=user)
        for action in actions:
            await self.remove_no_commit(session=session, pk=(action.id), user=user)

    async def create_or_update_no_commit(self, session: AsyncSession, *, obj_in: AppActionCore, user: User) -> AppAction:
        # Check if app with same name and version exists
        statement = select(self.model).where(
            self.model.name == obj_in.name,
            self.model.appId == obj_in.appId,
            self.model.appVersion == obj_in.appVersion
        )
        result = await session.exec(statement)
        existing_action = result.first()

        if existing_action:
            return await self.update_no_commit(
                session=session,
                db_obj=existing_action,
                obj_in=obj_in,
                user=user
            )

        return await self.create_no_commit(
            session=session,
            obj_in=obj_in,
            user=user
        )

app_action = CRUDAppAction(AppAction)
