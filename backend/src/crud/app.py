from typing import Optional
from sqlmodel import select
from src.models.base import TenantModel
from src.utils.auth import User
from .base import CRUDBase
from src.adk.models.app import AppCore
from src.db.models import App

class CRUDApp(CRUDBase[App, AppCore, AppCore]):
    async def create_or_update(self, session, *, obj_in: AppCore) -> App:
        # Use system user for app syncing
        system_user = User(id="system-user", email="support@trata.ai", role="system", tenantModel=TenantModel(orgId="system-org"))

        # Check if app with same name and version exists
        statement = select(self.model).where(
            self.model.name == obj_in.name,
            self.model.version == obj_in.version
        )
        result = await session.exec(statement)
        existing_app = result.first()

        if existing_app:
            return await self.update(
                session=session,
                db_obj=existing_app,
                obj_in=obj_in,
                user=system_user
            )

        return await self.create(
            session=session,
            obj_in=obj_in,
            user=system_user
        )

app = CRUDApp(App, primary_keys=["id", "version"])
