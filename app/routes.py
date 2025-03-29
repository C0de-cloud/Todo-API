from typing import Annotated, List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import Tag, TagCreate, Todo, TodoCreate, TodoList, TodoUpdate
from app.dependencies import (
    get_database, pagination_params, todo_filter_params,
    validate_todo_exists, validate_tag_exists
)
from app.crud import (
    create_tag, create_todo, delete_tag, delete_todo,
    get_tags, get_tags_count, get_todos, get_todos_count,
    update_tag, update_todo
)

router = APIRouter()


# ----- Tag Routes -----

@router.post("/tags", response_model=Tag, status_code=status.HTTP_201_CREATED)
async def create_tag_route(
    tag_data: Annotated[TagCreate, Body(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """Создать новый тег."""
    return await create_tag(db, tag_data.model_dump())


@router.get("/tags", response_model=List[Tag])
async def get_tags_route(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    pagination: Annotated[dict, Depends(pagination_params)]
):
    """Получить список тегов."""
    return await get_tags(db, pagination["limit"], pagination["offset"])


@router.get("/tags/{tag_id}", response_model=Tag)
async def get_tag_route(
    tag: Annotated[dict, Depends(validate_tag_exists)]
):
    """Получить тег по ID."""
    return tag


@router.put("/tags/{tag_id}", response_model=Tag)
async def update_tag_route(
    tag_data: Annotated[TagCreate, Body(...)],
    tag_id: Annotated[str, Path(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """Обновить тег."""
    updated_tag = await update_tag(db, tag_id, tag_data.model_dump())
    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_id} не найден"
        )
    return updated_tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_route(
    tag: Annotated[dict, Depends(validate_tag_exists)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """Удалить тег."""
    await delete_tag(db, tag["id"])
    return None


# ----- Todo Routes -----

@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo_route(
    todo_data: Annotated[TodoCreate, Body(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """Создать новую задачу."""
    return await create_todo(db, todo_data)


@router.get("/todos", response_model=TodoList)
async def get_todos_route(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    pagination: Annotated[dict, Depends(pagination_params)],
    filters: Annotated[dict, Depends(todo_filter_params)]
):
    """Получить список задач с пагинацией и фильтрацией."""
    todos = await get_todos(
        db, 
        pagination["limit"], 
        pagination["offset"], 
        filters
    )
    total = await get_todos_count(db, filters)
    
    return {
        "total": total,
        "limit": pagination["limit"],
        "offset": pagination["offset"],
        "items": todos
    }


@router.get("/todos/{todo_id}", response_model=Todo)
async def get_todo_route(
    todo: Annotated[dict, Depends(validate_todo_exists)]
):
    """Получить задачу по ID."""
    return todo


@router.put("/todos/{todo_id}", response_model=Todo)
async def update_todo_route(
    todo_data: Annotated[TodoUpdate, Body(...)],
    todo_id: Annotated[str, Path(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """Обновить задачу."""
    updated_todo = await update_todo(db, todo_id, todo_data)
    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {todo_id} не найдена"
        )
    return updated_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_route(
    todo: Annotated[dict, Depends(validate_todo_exists)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """Удалить задачу."""
    await delete_todo(db, todo["id"])
    return None 