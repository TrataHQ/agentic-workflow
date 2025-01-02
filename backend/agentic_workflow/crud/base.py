from typing import Generic, TypeVar, Type, Optional, List, Protocol, Union
from sqlmodel import SQLModel, select
from fastapi.encoders import jsonable_encoder
from agentic_workflow.constants import SYSTEM_USER
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.utils.auth import User
from sqlmodel import col


class HasIDAndOrgID(Protocol):
    id: str
    orgId: str


# Add a new type for primary key
PrimaryKeyType = Union[str, tuple]

ModelType = TypeVar("ModelType", bound=HasIDAndOrgID)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], primary_keys: List[str] = ["id"]):
        self.model = model
        self.primary_keys = primary_keys

    def _build_primary_key_filter(self, pk_value: PrimaryKeyType):
        # Handle both single and composite primary keys
        if isinstance(pk_value, tuple):
            if len(pk_value) != len(self.primary_keys):
                raise ValueError("Invalid primary key values")
            return [getattr(self.model, key) == value for key, value in zip(self.primary_keys, pk_value)]
        return [getattr(self.model, self.primary_keys[0]) == pk_value]

    async def get(self, session: AsyncSession, pk: PrimaryKeyType, user: User) -> Optional[ModelType]:
        pk_filters = self._build_primary_key_filter(pk)
        statement = select(self.model).where(
            col(self.model.orgId).in_([user.tenantModel.orgId, SYSTEM_USER.tenantModel.orgId]),
            *pk_filters,
        )
        result = await session.exec(statement)
        return result.first()

    async def get_multi(self, session: AsyncSession, *, skip: int = 0, limit: int = 100, user: User) -> List[ModelType]:
        statement = (
            select(self.model)
            .where(col(self.model.orgId).in_([user.tenantModel.orgId, SYSTEM_USER.tenantModel.orgId]))
            .offset(skip)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType, user: User) -> ModelType:
        return await self.create_no_commit(session, obj_in=obj_in, user=user, auto_commit=True)

    async def create_no_commit(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        user: User,
        auto_commit: bool = False,
    ) -> ModelType:
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

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        user: User,
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        setattr(db_obj, "updatedBy", user.id)

        # Build primary key filter for the select statement
        pk_values = tuple(getattr(db_obj, key) for key in self.primary_keys)
        pk_filters = self._build_primary_key_filter(pk_values)

        statement = select(self.model).where(
            col(self.model.orgId).in_([user.tenantModel.orgId, SYSTEM_USER.tenantModel.orgId]),
            *pk_filters,
        )
        result = await session.exec(statement)
        db_obj_current = result.first()

        if db_obj_current:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update_no_commit(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        user: User,
        auto_commit: bool = False,
    ) -> ModelType:
        if db_obj.orgId not in [user.tenantModel.orgId, SYSTEM_USER.tenantModel.orgId]:
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

    async def remove(self, session: AsyncSession, *, pk: PrimaryKeyType, user: User) -> None:
        await self.remove_no_commit(session=session, pk=pk, user=user, auto_commit=True)

    async def remove_no_commit(
        self,
        session: AsyncSession,
        *,
        pk: PrimaryKeyType,
        user: User,
        auto_commit: bool = False,
    ) -> None:
        pk_filters = self._build_primary_key_filter(pk)
        statement = select(self.model).where(
            col(self.model.orgId).in_([user.tenantModel.orgId, SYSTEM_USER.tenantModel.orgId]),
            *pk_filters,
        )
        result = await session.exec(statement)
        obj = result.first()
        if obj:
            await session.delete(obj)
            if auto_commit:
                await session.commit()
