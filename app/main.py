from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator

from app.database import create_tasks_table, database_cursor


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        if len(value) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return value


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        if len(value) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return value


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tasks_table()
    yield


app = FastAPI(title="Tasks API", lifespan=lifespan)


def task_not_found(task_id: int) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    with database_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
            (task.title, task.description, task.status.value),
        )
        task_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, title, description, status, created_at FROM tasks WHERE id = %s",
            (task_id,),
        )
        return cursor.fetchone()


@app.get("/tasks")
def list_tasks():
    with database_cursor() as cursor:
        cursor.execute(
            "SELECT id, title, description, status, created_at FROM tasks ORDER BY id"
        )
        return cursor.fetchall()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with database_cursor() as cursor:
        cursor.execute(
            "SELECT id, title, description, status, created_at FROM tasks WHERE id = %s",
            (task_id,),
        )
        task = cursor.fetchone()
    if task is None:
        raise task_not_found(task_id)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    with database_cursor(commit=True) as cursor:
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        if cursor.fetchone() is None:
            raise task_not_found(task_id)
        cursor.execute(
            "UPDATE tasks SET title = %s, description = %s, status = %s WHERE id = %s",
            (task.title, task.description, task.status.value, task_id),
        )
        cursor.execute(
            "SELECT id, title, description, status, created_at FROM tasks WHERE id = %s",
            (task_id,),
        )
        return cursor.fetchone()


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with database_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        if cursor.rowcount == 0:
            raise task_not_found(task_id)
