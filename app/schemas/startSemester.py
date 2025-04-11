from pydantic import BaseModel
from typing import List


class Elective(BaseModel):
    title: str
    option: str
    code: str


class StartSemesterData(BaseModel):
    user_id: int
    semester_title: str
    start_date: str
    end_date: str
    electives: List[Elective]


class GetAllSemesters(BaseModel):
    user_id: int


class GetAllCourses(BaseModel):
    user_id: int
    semester_id: int


class GetCourseStatistics(BaseModel):
    user_id: int
    semester_id: int
    course_id: int
