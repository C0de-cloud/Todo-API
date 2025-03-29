from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.models import TodoCreate, TodoUpdate


def get_todos_collection(db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
    """Получение коллекции задач."""
    return db.todos


def get_tags_collection(db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
    """Получение коллекции тегов."""
    return db.tags


# ----- Tag CRUD Operations -----

async def create_tag(db: AsyncIOMotorDatabase, tag_data: dict) -> dict:
    """Создание нового тега."""
    tag_collection = get_tags_collection(db)
    result = await tag_collection.insert_one(tag_data)
    return {**tag_data, "id": str(result.inserted_id)}


async def get_tag_by_id(db: AsyncIOMotorDatabase, tag_id: str) -> Optional[dict]:
    """Получение тега по ID."""
    try:
        tag_collection = get_tags_collection(db)
        tag = await tag_collection.find_one({"_id": ObjectId(tag_id)})
        if tag:
            tag["id"] = str(tag["_id"])
            del tag["_id"]
        return tag
    except Exception:
        return None


async def get_tags(db: AsyncIOMotorDatabase, limit: int = 100, offset: int = 0) -> List[dict]:
    """Получение списка тегов с пагинацией."""
    tag_collection = get_tags_collection(db)
    cursor = tag_collection.find().skip(offset).limit(limit)
    tags = []
    async for tag in cursor:
        tag["id"] = str(tag["_id"])
        del tag["_id"]
        tags.append(tag)
    return tags


async def get_tags_count(db: AsyncIOMotorDatabase) -> int:
    """Получение общего количества тегов."""
    tag_collection = get_tags_collection(db)
    return await tag_collection.count_documents({})


async def update_tag(db: AsyncIOMotorDatabase, tag_id: str, tag_data: dict) -> Optional[dict]:
    """Обновление тега."""
    try:
        tag_collection = get_tags_collection(db)
        result = await tag_collection.update_one(
            {"_id": ObjectId(tag_id)},
            {"$set": tag_data}
        )
        if result.modified_count > 0:
            return await get_tag_by_id(db, tag_id)
        return None
    except Exception:
        return None


async def delete_tag(db: AsyncIOMotorDatabase, tag_id: str) -> bool:
    """Удаление тега."""
    try:
        tag_collection = get_tags_collection(db)
        result = await tag_collection.delete_one({"_id": ObjectId(tag_id)})
        
        # Также удаляем ссылки на тег из всех задач
        todo_collection = get_todos_collection(db)
        await todo_collection.update_many(
            {"tags": {"$in": [ObjectId(tag_id)]}},
            {"$pull": {"tags": ObjectId(tag_id)}}
        )
        
        return result.deleted_count > 0
    except Exception:
        return False


# ----- Todo CRUD Operations -----

async def create_todo(db: AsyncIOMotorDatabase, todo_data: TodoCreate) -> dict:
    """Создание новой задачи."""
    now = datetime.utcnow()
    
    # Преобразование строковых ID тегов в ObjectId
    tag_ids = [ObjectId(tag_id) for tag_id in todo_data.tags if tag_id]
    
    todo_dict = todo_data.model_dump(exclude={"tags"})
    todo_dict.update({
        "created_at": now,
        "updated_at": now,
        "tags": tag_ids
    })
    
    todo_collection = get_todos_collection(db)
    result = await todo_collection.insert_one(todo_dict)
    
    # Получаем созданную задачу с полной информацией о тегах
    return await get_todo_by_id(db, str(result.inserted_id))


async def get_todo_by_id(db: AsyncIOMotorDatabase, todo_id: str) -> Optional[dict]:
    """Получение задачи по ID с полной информацией о тегах."""
    try:
        todo_collection = get_todos_collection(db)
        todo = await todo_collection.find_one({"_id": ObjectId(todo_id)})
        
        if todo:
            todo["id"] = str(todo["_id"])
            del todo["_id"]
            
            # Получаем полную информацию о тегах
            tag_collection = get_tags_collection(db)
            tag_ids = [tag_id for tag_id in todo.get("tags", [])]
            
            if tag_ids:
                tags = []
                async for tag in tag_collection.find({"_id": {"$in": tag_ids}}):
                    tag["id"] = str(tag["_id"])
                    del tag["_id"]
                    tags.append(tag)
                todo["tags"] = tags
            else:
                todo["tags"] = []
                
            return todo
        return None
    except Exception:
        return None


async def get_todos(
    db: AsyncIOMotorDatabase, 
    limit: int = 10, 
    offset: int = 0,
    filters: dict = None
) -> List[dict]:
    """Получение списка задач с пагинацией и фильтрацией."""
    todo_collection = get_todos_collection(db)
    
    # Применяем фильтры, если они указаны
    query = filters or {}
    
    if "tags" in query and isinstance(query["tags"], dict) and "$elemMatch" in query["tags"]:
        # Преобразуем строковый ID тега в ObjectId для запроса
        tag_id = query["tags"]["$elemMatch"]["$eq"]
        query["tags"] = {"$elemMatch": {"$eq": ObjectId(tag_id)}}
    
    cursor = todo_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
    
    todos = []
    async for todo in cursor:
        todo["id"] = str(todo["_id"])
        del todo["_id"]
        
        # Получаем полную информацию о тегах
        tag_collection = get_tags_collection(db)
        tag_ids = [tag_id for tag_id in todo.get("tags", [])]
        
        if tag_ids:
            tags = []
            async for tag in tag_collection.find({"_id": {"$in": tag_ids}}):
                tag["id"] = str(tag["_id"])
                del tag["_id"]
                tags.append(tag)
            todo["tags"] = tags
        else:
            todo["tags"] = []
            
        todos.append(todo)
        
    return todos


async def get_todos_count(db: AsyncIOMotorDatabase, filters: dict = None) -> int:
    """Получение общего количества задач с учетом фильтров."""
    todo_collection = get_todos_collection(db)
    query = filters or {}
    
    if "tags" in query and isinstance(query["tags"], dict) and "$elemMatch" in query["tags"]:
        # Преобразуем строковый ID тега в ObjectId для запроса
        tag_id = query["tags"]["$elemMatch"]["$eq"]
        query["tags"] = {"$elemMatch": {"$eq": ObjectId(tag_id)}}
        
    return await todo_collection.count_documents(query)


async def update_todo(db: AsyncIOMotorDatabase, todo_id: str, todo_data: TodoUpdate) -> Optional[dict]:
    """Обновление задачи."""
    try:
        todo_collection = get_todos_collection(db)
        
        # Исключаем None значения из обновления
        update_data = {k: v for k, v in todo_data.model_dump(exclude_unset=True).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Обработка тегов
        if "tags" in update_data:
            update_data["tags"] = [ObjectId(tag_id) for tag_id in update_data["tags"]]
        
        result = await todo_collection.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await get_todo_by_id(db, todo_id)
        return None
    except Exception:
        return None


async def delete_todo(db: AsyncIOMotorDatabase, todo_id: str) -> bool:
    """Удаление задачи."""
    try:
        todo_collection = get_todos_collection(db)
        result = await todo_collection.delete_one({"_id": ObjectId(todo_id)})
        return result.deleted_count > 0
    except Exception:
        return False 