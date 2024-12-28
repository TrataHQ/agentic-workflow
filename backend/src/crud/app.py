from typing import Optional
from sqlmodel import select
from src.models.base import TenantModel
from src.utils.auth import User
from .base import CRUDBase
from src.adk.models.app import AppEntity
from src.db.models import App
from sqlmodel.ext.asyncio.session import AsyncSession
from src.constants import SYSTEM_USER


class CRUDApp(CRUDBase[App, AppEntity, AppEntity]):
    async def create_or_update_no_commit(self, session: AsyncSession, *, obj_in: AppEntity, user: User) -> App:
        # Check if app with same name and version exists
        statement = select(self.model).where(
            self.model.name == obj_in.name,
            self.model.version == obj_in.version
        )
        result = await session.exec(statement)
        existing_app = result.first()

        if existing_app:
            return await self.update_no_commit(
                session=session,
                db_obj=existing_app,
                obj_in=obj_in,
                user=user
            )

        return await self.create_no_commit(
            session=session,
            obj_in=obj_in,
            user=user
        )

app = CRUDApp(App, primary_keys=["id", "version"])
