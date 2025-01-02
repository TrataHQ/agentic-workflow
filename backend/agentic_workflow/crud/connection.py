from typing import List
from agentic_workflow.crud.base import CRUDBase
from agentic_workflow.adk.models.connection import ConnectionCore
from agentic_workflow.db.models import Connection
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from agentic_workflow.utils.auth import User


class CRUDConnection(CRUDBase[Connection, ConnectionCore, ConnectionCore]):
    async def get_by_app_id(
        self, session: AsyncSession, *, app_id: str, version: str, user: User
    ) -> List[Connection]:
        """
        Retrieve all connections associated with a specific app_id
        """
        statement = (
            select(self.model)
            .where(self.model.appId == app_id)
            .where(self.model.appVersion == version)
            .where(self.model.orgId == user.tenantModel.orgId)
        )
        result = await session.exec(statement)
        return list(result.all())


connection = CRUDConnection(Connection)
