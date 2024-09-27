from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from ..models.base import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from ..models.base import AsyncSessionLocal
from sqlalchemy import select

Session = sessionmaker(bind=async_engine)

@asynccontextmanager
async def async_session_scope():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def create_object(model, **kwargs):
    """Create a new object and add it to the database."""
    async with async_session_scope() as session:
        obj = model(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

async def get_object(model, object_id):
    """Retrieve an object by its ID from the database."""
    async with async_session_scope() as session:
        return await session.get(model, object_id)


async def update_object(model, object_id, **kwargs):
    """Update attributes of an existing object."""
    async with async_session_scope() as session:
        obj = await session.get(model, object_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)

async def delete_object(model, object_id):
    """Delete an object from the database."""
    async with async_session_scope() as session:
        obj = await session.get(model, object_id)
        if obj:
            await session.delete(obj)

async def get_object_by(model, **filters):
    """Retrieve a single object from the database matching the provided filters."""
    async with async_session_scope() as session:
        result = await session.execute(select(model).filter_by(**filters))
        return result.scalars().first()

async def list_objects(model, **filters):
    """List objects from the database that match the provided filters."""
    async with async_session_scope() as session:
        return await session.execute(session.query(model).filter_by(**filters))