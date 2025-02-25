
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from db.student_service import StudentService
from schemes.student import StudentUpdate, StudentResponse

student_router = APIRouter(prefix="/students", tags=["students"])
student_service = StudentService()

@student_router.get("")
async def get_students():
    return {
        "message": "We are students!"
    }

@student_router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int):
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    return student

@student_router.post("", response_model=StudentResponse)
async def create_student(student_data: StudentUpdate):
    created_student = await student_service.create_student(student_data)
    return created_student

@student_router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_data: StudentUpdate):
    updated_student = await student_service.update_student(student_id, student_data)
    if not updated_student:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    return updated_student

@student_router.delete("/{student_id}", response_model=dict)
async def get_student(student_id: int):
    deleted = await student_service.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Student not found")
    return {
        "message": "Student was deleted."
    }
