import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from db.student_service import StudentService
from db.auth_service import AuthService
from db.db_conf import Base, PG_URL
from schemes.user import UserCreate

async def create_db():
    engine = create_async_engine(PG_URL, echo=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

async def main():
    await create_db()
    student_service = StudentService(PG_URL)
    auth_service = AuthService(PG_URL)
    await student_service.insert_from_csv("students.csv")
    await auth_service.create_user(UserCreate(username='vasya', password='pupkin'))

if __name__ == "__main__":
    asyncio.run(main())
