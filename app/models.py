from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field("#0ea5e9", pattern=r"^#[0-9a-fA-F]{6}$")


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: str = Field(...)
    
    model_config = ConfigDict(populate_by_name=True)


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: bool = Field(False)
    due_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    tags: List[str] = Field(default=[])  # IDs тегов


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None  # IDs тегов


class Todo(TodoBase):
    id: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    tags: List[Tag] = Field(default=[])
    
    model_config = ConfigDict(populate_by_name=True)


class TodoList(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[Todo] 