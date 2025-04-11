# app/schemas/course_start.py
from pydantic import BaseModel


class StartSemesterData(BaseModel):
    user_id: int
    semester_title: str
    start_date: str
    end_date: str


class GetAllSemesters(BaseModel):
    user_id: int


class GetAllCourses(BaseModel):
    user_id: int
    semester_id: int


class GetCourseStatistics(BaseModel):
    user_id: int
    semester_id: int
    course_id: int
