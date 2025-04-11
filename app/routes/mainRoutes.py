from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
import json

router = APIRouter(prefix="/main", tags=["StartSemester"])


@router.get("/hello")
def print_hello():
    return {"message": "Hello from the main route!"}


@router.post("/startSemester")
def startSemester(db: Session = Depends(get_db)):
    with open("../data/courseRoadmap.json", "r") as file:
        courseRoadmap = json.load(file)

    print(courseRoadmap)  # Debugging line to check the loaded data
    return courseRoadmap
