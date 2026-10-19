from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Title of the task",
        examples=["Buy groceries"],
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Detailed explanation of the task",
        examples=["Milk, sourdough bread, and eggs"],
    )
    completed: bool = Field(
        default=False,
        description="Status flag showing completion",
        examples=[False],
    )


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=120, examples=["Buy groceries"]
    )
    description: Optional[str] = Field(
        None, max_length=500, examples=["Updated items list"]
    )
    completed: Optional[bool] = Field(None, examples=[True])


class TodoResponse(TodoBase):
    id: int = Field(..., description="Unique database identifier", examples=[1])
    created_at: datetime = Field(
        ..., description="Timestamp when task was created"
    )

    model_config = ConfigDict(from_attributes=True)