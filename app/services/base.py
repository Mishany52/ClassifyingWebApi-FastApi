from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
    async def getById(self, db: AsyncSession, obj_id: Any):
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await db.execute(stmt)
        obj_db = result.scalars().first()
        
        if not obj_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Object with id {obj_id} not found")
        
        return obj_db    
        
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[Type[ModelType]]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def get_multi(
    self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(
        self, db: AsyncSession, id: Any, obj_in: UpdateSchemaType
    ) -> ModelType:
            db_obj:ModelType = await self.getById(db, id) 
            update_data = jsonable_encoder(obj_in)
            
            for key, value in update_data.items():
                setattr(db_obj, key, value)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        
    async def remove(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        db_obj:ModelType = await self.getById(db, id) 
        await db.delete(db_obj)
        await db.commit()
        return  db_obj    

