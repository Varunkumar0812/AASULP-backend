# app/schemas/course_start.py
from pydantic import BaseModel


class StartSemesterData(BaseModel):
    user_id: int
    semester_title: str
    start_date: str
    end_date: str
