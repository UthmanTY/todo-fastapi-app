from typing import List
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
import models
import schemas
from sqlalchemy.orm import Session

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do List REST API",
    description="A robust, production-ready CRUD To-Do List API built with FastAPI and SQLite.",
    version="1.0.0",
    docs_url="/docs",  # Interactive Swagger UI
    redoc_url="/redoc",  # Alternative ReDoc documentation
)

# Enable CORS for public consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Root"],
    summary="Health check / API Welcome",
    description="Quick endpoint to verify API availability.",
)
def root():
    return {
        "status": "online",
        "docs_url": "/docs",
        "message": "Welcome to the To-Do API",
    }


# ---------------------- CREATE ----------------------
@app.post(
    "/todos",
    response_model=schemas.TodoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["To-Dos"],
    summary="Create a new task",
    description="Accepts a payload with task details and stores it in the database.",
)
def create_todo(
    todo: schemas.TodoCreate, db: Session = Depends(get_db)
):
    db_item = models.TodoItem(**todo.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# ---------------------- READ ALL ----------------------
@app.get(
    "/todos",
    response_model=List[schemas.TodoResponse],
    tags=["To-Dos"],
    summary="List all tasks",
    description="Retrieve all stored tasks with optional pagination limits and skips.",
)
def read_todos(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max items per page"),
    db: Session = Depends(get_db),
):
    return db.query(models.TodoItem).offset(skip).limit(limit).all()


# ---------------------- READ ONE ----------------------
@app.get(
    "/todos/{todo_id}",
    response_model=schemas.TodoResponse,
    tags=["To-Dos"],
    summary="Get a single task by ID",
    description="Retrieve specific details of a to-do item by providing its numerical identifier.",
)
def read_todo(
    todo_id: int = Path(..., ge=1, description="The ID of the task to fetch"),
    db: Session = Depends(get_db),
):
    db_item = (
        db.query(models.TodoItem).filter(models.TodoItem.id == todo_id).first()
    )
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-Do with ID {todo_id} was not found",
        )
    return db_item


# ---------------------- UPDATE ----------------------
@app.put(
    "/todos/{todo_id}",
    response_model=schemas.TodoResponse,
    tags=["To-Dos"],
    summary="Update an existing task",
    description="Perform a partial or full update on a task. Fields omitted in the payload remain unchanged.",
)
def update_todo(
    todo_id: int = Path(..., ge=1, description="The ID of the task to update"),
    payload: schemas.TodoUpdate = ...,
    db: Session = Depends(get_db),
):
    db_item = (
        db.query(models.TodoItem).filter(models.TodoItem.id == todo_id).first()
    )
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-Do with ID {todo_id} was not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


# ---------------------- DELETE ----------------------
@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["To-Dos"],
    summary="Delete a task",
    description="Removes a specific task permanently from the database.",
)
def delete_todo(
    todo_id: int = Path(..., ge=1, description="The ID of the task to delete"),
    db: Session = Depends(get_db),
):
    db_item = (
        db.query(models.TodoItem).filter(models.TodoItem.id == todo_id).first()
    )
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"To-Do with ID {todo_id} was not found",
        )

    db.delete(db_item)
    db.commit()
    return None