from typing import Generic, TypeVar, Type, Optional, List, Protocol, Union
from sqlmodel import SQLModel, select
from fastapi.encoders import jsonable_encoder
from src.models.base import TenantModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.utils.auth import User

class HasIDAndOrgID(Protocol):
    id: str
    orgId: str

ModelType = TypeVar("ModelType", bound=HasIDAndOrgID)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: str, user: User) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.orgId == user.tenantModel.orgId, self.model.id == id)
        result = await session.exec(statement)
        return result.first()

    async def get_multi(self, session: AsyncSession, *, skip: int = 0, limit: int = 100, user: User) -> List[ModelType]:
        statement = select(self.model).where(self.model.orgId == user.tenantModel.orgId).offset(skip).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType, user: User) -> ModelType:
        return await self.create_no_commit(session, obj_in=obj_in, user=user, auto_commit=True)

    async def create_no_commit(self, session: AsyncSession, *, obj_in: CreateSchemaType, user: User, auto_commit: bool = False) -> ModelType:
        obj_data = jsonable_encoder(obj_in)
        obj_data["orgId"] = user.tenantModel.orgId
        obj_data["createdBy"] = user.id
        obj_data["updatedBy"] = user.id
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        if auto_commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(self, session: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType, user: User) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        setattr(db_obj, "updatedBy", user.id)

        statement = select(self.model).where(
            self.model.orgId == user.tenantModel.orgId,
            self.model.id == db_obj.id
        )
        result = await session.exec(statement)
        db_obj_current = result.first()
        
        if db_obj_current:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update_no_commit(self, session: AsyncSession, *, db_obj: ModelType, obj_in: UpdateSchemaType, user: User, auto_commit: bool = False) -> ModelType:
        if db_obj.orgId != user.tenantModel.orgId:
            raise ValueError("Not authorized to update this object")
            
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        session.add(db_obj)
        
        if auto_commit:
            await session.commit()
            await session.refresh(db_obj)
        
        return db_obj

    async def remove(self, session: AsyncSession, *, id: str, user: User) -> None:
        statement = select(self.model).where(self.model.orgId == user.tenantModel.orgId, self.model.id == id)
        result = await session.exec(statement)
        obj = result.first()
        if obj:
            await session.delete(obj)
            await session.commit()
