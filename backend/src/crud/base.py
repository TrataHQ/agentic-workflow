from typing import Generic, TypeVar, Type, Optional, List
from sqlmodel import SQLModel, select
from fastapi.encoders import jsonable_encoder
from backend.src.models.base import TenantModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, session, id: int, tenantModel: TenantModel) -> Optional[ModelType]:
        return session.get(self.model, id).where(self.model.orgId == tenantModel.orgId)

    def get_multi(self, session, *, skip: int = 0, limit: int = 100, tenantModel: TenantModel) -> List[ModelType]:
        statement = select(self.model).where(self.model.orgId == tenantModel.orgId).offset(skip).limit(limit)
        return session.exec(statement).all()

    def create(self, session, *, obj_in: CreateSchemaType, tenantModel: TenantModel) -> ModelType:
        return self.create_no_commit(session, obj_in=obj_in, tenant=tenantModel, auto_commit=True)

    def create_no_commit(self, session, *, obj_in: CreateSchemaType, tenant: TenantModel, auto_commit: bool = False) -> ModelType:
        obj_data = jsonable_encoder(obj_in)
        obj_data["org_id"] = tenant.org_id
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        
        if auto_commit:
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def update(self, session, *, db_obj: ModelType, obj_in: UpdateSchemaType, tenantModel: TenantModel) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        session.add(db_obj).where(self.model.orgId == tenantModel.orgId)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_no_commit(self, session, *, db_obj: ModelType, obj_in: UpdateSchemaType, tenant: TenantModel, auto_commit: bool = False) -> ModelType:
        if db_obj.org_id != tenant.org_id:
            raise ValueError("Not authorized to update this object")
            
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        session.add(db_obj)
        
        if auto_commit:
            session.commit()
            session.refresh(db_obj)
        
        return db_obj

    def remove(self, session, *, id: int, tenantModel: TenantModel) -> ModelType:
        obj = session.get(self.model, id).where(self.model.orgId == tenantModel.orgId)
        session.delete(obj)
        session.commit()
        return obj
