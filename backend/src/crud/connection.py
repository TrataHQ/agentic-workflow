from typing import List
from src.crud.base import CRUDBase
from src.models.connection import ConnectionCore
from src.db.models.models import Connection
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.utils.auth import User

class CRUDConnection(CRUDBase[Connection, ConnectionCore, ConnectionCore]):
    async def get_by_app_id(self, session: AsyncSession, *, app_id: str, user: User) -> List[Connection]:
        """
        Retrieve all connections associated with a specific app_id
        """
        statement = select(self.model).where(self.model.appId == app_id).where(self.model.orgId == user.tenantModel.orgId)
        result = await session.exec(statement)
        return list(result.all())

connection = CRUDConnection(Connection)
