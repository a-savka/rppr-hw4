import aioredis
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from http import HTTPStatus
from db.student_service import StudentService
from schemes.student import StudentUpdate, StudentResponse
from db.models.user_model import User
import os
import json
from pydantic import BaseModel

student_router = APIRouter(prefix="/students", tags=["students"])
student_service = StudentService()

from .auth_middleware import get_current_user

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Определяем корень проекта

# Redis setup
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True)


class FilePathRequest(BaseModel):
    file_path: str

@student_router.get("")
async def get_students(user: User = Depends(get_current_user)):
    return {
        "message": "We are students!"
    }


@student_router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, user: User = Depends(get_current_user)):
    # Check cache first
    cached_student = await redis.get(f"student:{student_id}")
    if cached_student:
        return json.loads(cached_student)  # Return the cached data

    # If not in cache, fetch from DB
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    
    # Serialize student to dict (use a custom serialization function for SQLAlchemy model)
    student_dict = student_to_dict(student)

    # Cache the student data
    await redis.set(f"student:{student_id}", json.dumps(student_dict), ex=3600)  # Cache for 1 hour

    return student_dict

def student_to_dict(student) -> dict:
    """Convert the SQLAlchemy Student object to a dict for caching."""
    return {
        "id": student.id,
        "last_name": student.last_name,
        "first_name": student.first_name,
        "faculty": student.faculty,
        "course": student.course,
        "grade": student.grade,
    }

@student_router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, user: User = Depends(get_current_user)):
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    return student

@student_router.post("", response_model=StudentResponse)
async def create_student(student_data: StudentUpdate, user: User = Depends(get_current_user)):
    created_student = await student_service.create_student(student_data)
    return created_student

@student_router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_data: StudentUpdate, user: User = Depends(get_current_user)):
    updated_student = await student_service.update_student(student_id, student_data)
    if not updated_student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    return updated_student

@student_router.delete("/{student_id}", response_model=dict)
async def get_student(student_id: int, user: User = Depends(get_current_user)):
    deleted = await student_service.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    return {
        "message": "Student was deleted."
    }

async def load_data(file_path: str):
    resolved_path = os.path.join(BASE_DIR, "..", "..", file_path)
    resolved_path = os.path.abspath(resolved_path)
    await student_service.insert_from_csv(resolved_path)

@student_router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, request: FilePathRequest):
    background_tasks.add_task(load_data, request.file_path)
    return {"message": "Загрузка данных запущена", "file_path": request.file_path}

@student_router.post("/delete-many")
async def delete_students(background_tasks: BackgroundTasks, ids: dict):
    async def delete_task(ids_list: list):
        for student_id in ids_list:
            deleted = await student_service.delete_student(student_id)
            if not deleted:
                print(f"Student with ID {student_id} not found for deletion.")

    background_tasks.add_task(delete_task, ids['ids'])
    return {"message": "Students deletion started", "ids": ids['ids']}

