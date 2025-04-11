from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.models import Course, Semester, Exam, Week, Topic
from app.schemas.startSemester import StartSemesterData
import json
from app.utils.llm import getCourseRoadmap


router = APIRouter()


# Get All Semesters
@router.get("/getAllSemesters")
def getAllSemesters(db: Session = Depends(get_db)):
    semesters = db.query(Semester).all()

    for semester in semesters:
        courses = (
            db.query(Course).filter(Course.semester_id == semester.semester_id).all()
        )

        total_credits = 0
        weighted_score = 0
        is_ongoing = False

        for course in courses:
            total_credits += course.credit or 0  # to handle None credits

            if course.status == "Active":
                is_ongoing = True

            if course.mark is not None:  # to handle None marks
                weighted_score += course.credit * course.mark

        # Set calculated attributes
        semester.credits = total_credits
        semester.status = "OnGoing" if is_ongoing else "Completed"

        if total_credits > 0:
            semester.gpa = round(weighted_score / total_credits, 2)
        else:
            semester.gpa = None  # or 0.0 if preferred

    return semesters


# Initiate a Semester
@router.post("/startSemester")
def startSemester(
    payload: StartSemesterData,
    db: Session = Depends(get_db),
):
    # Step 1: Load all semester data from your JSON file
    with open(
        "C:/Users/tvaru/Desktop/AI-ASULP/app/data/semester_course_details.json", "r"
    ) as file:
        data = json.load(file)

    # Step 2: Find the semester matching the input title
    matched_semester = next(
        (s for s in data if s.get("title") == payload.semester_title),
        None,
    )

    if not matched_semester:
        raise HTTPException(status_code=404, detail="Semester not found in roadmap")

    # Step 3: Create the Semester in DB
    semester = Semester(
        title=matched_semester.get("title"),
        user_id=payload.user_id,
        gpa=0.0,
    )

    db.add(semester)
    db.commit()
    db.refresh(semester)

    semester_data = {
        "title": semester.title,
        "start_date": payload.start_date,
        "end_date": payload.end_date,
    }

    # Step 4: Loop through each course and insert it
    for course_item in matched_semester.get("courses", []):
        courseRoadmap = getCourseRoadmap(semester_data, course_item)

        course = Course(
            title=courseRoadmap.get("title"),
            code=courseRoadmap.get("code"),
            description=courseRoadmap.get("description"),
            credit=courseRoadmap.get("credit"),
            periods=courseRoadmap.get("periods"),
            start_date=courseRoadmap.get("start_date"),
            end_date=courseRoadmap.get("end_date"),
            status=courseRoadmap.get("status"),
            user_id=payload.user_id,
            semester_id=semester.semester_id,
            type=courseRoadmap.get("type"),
        )

        db.add(course)
        db.commit()
        db.refresh(course)

        # Step 5: Create Exams for each course
        for exam_data in courseRoadmap.get("Exams", []):
            exam = Exam(
                title=exam_data.get("title"),
                type=exam_data.get("type"),
                rank=exam_data.get("rank"),
                start_date=exam_data.get("start_date"),
                end_date=exam_data.get("end_date"),
                status=exam_data.get("status"),
                course_id=course.course_id,
                user_id=payload.user_id,
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)

        # Step 6: Create Weeks & Topics for each course
        for week_data in courseRoadmap.get("Weeks", []):
            week = Week(
                title=week_data.get("title"),
                rank=week_data.get("rank"),
                status=week_data.get("status"),
                course_id=course.course_id,
                user_id=payload.user_id,
            )
            db.add(week)
            db.commit()
            db.refresh(week)

            for topic_data in week_data.get("Topics", []):
                topic = Topic(
                    title=topic_data.get("title"),
                    description=topic_data.get("description"),
                    week_id=week.week_id,
                )
                db.add(topic)
                db.commit()
                db.refresh(topic)

    return {"status": 200, "message": "Semester and all courses successfully created"}
