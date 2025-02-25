from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from db.db_conf import Base

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    faculty = Column(String, nullable=False)
    course = Column(String, nullable=False)
    grade = Column(Float, nullable=False)
