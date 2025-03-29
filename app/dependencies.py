from typing import Annotated
from fastapi import Depends, HTTPException, Path, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.crud import get_todo_by_id, get_tag_by_id


async def get_database() -> AsyncIOMotorDatabase:
    """Получение экземпляра базы данных."""
    from main import app
    return app.mongodb


async def validate_todo_exists(
    todo_id: Annotated[str, Path(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
) -> dict:
    """Проверка существования задачи по ID."""
    todo = await get_todo_by_id(db, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {todo_id} не найдена"
        )
    return todo


async def validate_tag_exists(
    tag_id: Annotated[str, Path(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
) -> dict:
    """Проверка существования тега по ID."""
    tag = await get_tag_by_id(db, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_id} не найден"
        )
    return tag


def pagination_params(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    """Параметры пагинации."""
    return {"limit": limit, "offset": offset}


def todo_filter_params(
    is_completed: bool = Query(None),
    tag_id: str = Query(None),
) -> dict:
    """Параметры фильтрации задач."""
    filters = {}
    if is_completed is not None:
        filters["is_completed"] = is_completed
    if tag_id:
        filters["tags"] = {"$elemMatch": {"$eq": tag_id}}
    return filters 