
from typing import Optional

import csv
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from schemes.student import StudentCreate, StudentUpdate
from db.models.student_model import Student
from db.db_conf import PG_URL

class StudentService:
    def __init__(self, db_url=PG_URL):
        self.engine = create_async_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def insert_student(self, last_name, first_name, faculty, course, grade):
        async with self.Session() as session:
            async with session.begin():
                student = Student(last_name=last_name, first_name=first_name, faculty=faculty, course=course, grade=grade)
                session.add(student)

    async def create_student(self, student_dto: StudentCreate):
        async with self.Session() as session:
            async with session.begin():
                student = Student(**student_dto.model_dump())
                session.add(student)
                await session.commit()
                return student


    async def update_student(self, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
        async with self.Session() as session:
            result = await session.execute(select(Student).where(Student.id == student_id))
            student = result.scalar_one_or_none()

            if not student:
                return None

            for key, value in student_data.model_dump(exclude_unset=True).items():
                setattr(student, key, value)

            await session.commit()
            await session.refresh(student)
            return student

    async def get_student_by_id(self, student_id: int) -> Optional[Student]:
        async with self.Session() as session:
            result = await session.execute(select(Student).where(Student.id == student_id))
            student = result.scalar_one_or_none()
            return student

    async def delete_student(self, student_id: int) -> bool:
        async with self.Session() as session:
            result = await session.execute(select(Student).where(Student.id == student_id))
            student = result.scalar_one_or_none()

            if not student:
                return False

            await session.delete(student)
            await session.commit()
            return True 

    async def insert_from_csv(self, file_path):
        async with self.Session() as session:
            async with session.begin():
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    students = [
                        Student(
                            last_name=row['Фамилия'],
                            first_name=row['Имя'],
                            faculty=row['Факультет'],
                            course=row['Курс'],
                            grade=float(row['Оценка'])
                        ) for row in reader
                    ]
                    session.add_all(students)

    async def get_students_by_faculty(self, faculty):
        async with self.Session() as session:
            result = await session.execute(
                select(Student).filter_by(faculty=faculty)
            )
            return result.scalars().all()

    async def get_unique_courses(self):
        async with self.Session() as session:
            result = await session.execute(
                select(distinct(Student.course))
            )
            return [c[0] for c in result.all()]

    async def get_average_grade_by_faculty(self, faculty):
        async with self.Session() as session:
            result = await session.execute(
                select(func.avg(Student.grade)).filter_by(faculty=faculty)
            )
            return result.scalar()

    async def get_students_with_low_grades(self, course, threshold=30):
        async with self.Session() as session:
            result = await session.execute(
                select(Student).filter(Student.course == course, Student.grade < threshold)
            )
            return result.scalars().all()