from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.models import Course, Semester, Exam, Week, Topic, Quiz
from app.schemas.startSemester import (
    StartSemesterData,
    GetAllSemesters,
    GetAllCourses,
    GetCourseStatistics,
)
import json
from app.utils.llm import getCourseRoadmap


router = APIRouter()


# Get Course Statistics
@router.get("/getCourseStatistics")
def getCourseStatistics(payload: GetCourseStatistics, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.course_id == payload.course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Getting all exams and weeks for the course
    exams = (
        db.query(Exam)
        .filter(Exam.course_id == course.course_id)
        .order_by(Exam.rank)
        .all()
    )

    weeks = (
        db.query(Week)
        .filter(Week.course_id == course.course_id)
        .order_by(Week.rank)
        .all()
    )

    # Set next_topic
    next_week = next((week for week in weeks if week.status == "Pending"), None)
    course.next_topic = next_week  # Will be serialized as object or dict

    # Quiz performance calculation
    total_quizzes = 0
    completed_quizzes = 0
    quiz_score = 0

    # Course progress calculation
    total_topics = 0
    completed_topics = 0

    for week in weeks:
        topics = (
            db.query(Topic)
            .filter(Topic.week_id == week.week_id)
            .order_by(Topic.title)
            .all()
        )
        quizzes = db.query(Quiz).filter(Quiz.week_id == week.week_id).all()

        week.quizzes = quizzes
        week.topics = topics

        quiz_performance = {}

        for quiz in quizzes:
            quiz_performance[quiz.quiz_id] = {
                "title": quiz.title,
                "status": quiz.status,
                "score": quiz.score,
            }

        total_topics += len(topics)
        completed_topics += sum(1 for topic in topics if topic.status == "Completed")
        total_quizzes += len(quizzes)
        completed_quizzes += sum(1 for quiz in quizzes if quiz.status == "Completed")
        quiz_score += sum(quiz.score for quiz in quizzes if quiz.status == "Completed")

    # Setting all additional variables to course object
    course.quiz_performance = quiz_performance
    course.total_quizzes = total_quizzes
    course.completed_quizzes = completed_quizzes
    course.avg_quiz_score = (
        round(quiz_score / total_quizzes, 2) if total_quizzes > 0 else 0
    )
    course.total_topics = total_topics
    course.completed_topics = completed_topics
    course.progress = (
        round((completed_topics / total_topics) * 100, 2) if total_topics > 0 else 0
    )
    course.exams = exams

    return course


@router.get("/getAllCourses")
def getAllCourses(payload: GetAllCourses, db: Session = Depends(get_db)):
    courses = (
        db.query(Course)
        .filter(
            Course.user_id == payload.user_id,
            Course.semester_id == payload.semester_id,
        )
        .all()
    )

    # Setting next topic and progress for each course
    for course in courses:
        weeks = (
            db.query(Week)
            .filter(Week.course_id == course.course_id)
            .order_by(Week.rank)
            .all()
        )

        # Set next_topic
        next_week = next((week for week in weeks if week.status == "Pending"), None)
        course.next_topic = next_week  # Will be serialized as object or dict

        # Progress calculation
        total_weeks = len(weeks)
        completed_weeks = sum(1 for week in weeks if week.status == "Completed")

        course.progress = (
            round((completed_weeks / total_weeks) * 100, 2) if total_weeks > 0 else 0
        )

    return courses


# Get All Semesters
@router.get("/getAllSemesters")
def getAllSemesters(payload: GetAllSemesters, db: Session = Depends(get_db)):
    semesters = db.query(Semester).filter(Semester.user_id == payload.user_id).all()

    for semester in semesters:
        courses = (
            db.query(Course)
            .filter(
                Course.semester_id == semester.semester_id
                and Course.user_id == payload.user_id
            )
            .all()
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

    with open(
        "C:/Users/tvaru/Desktop/AI-ASULP/app/data/semester_course_details.json", "r"
    ) as file:
        next_semester_data = json.load(file)[len(semesters)]

    print(next_semester_data)

    electives = []
    nxt_sem_title = next_semester_data["title"]

    for course in next_semester_data["courses"]:
        if course["code"] == "":
            electives.append(
                {
                    "title": course["title"],
                    "choices": course["choices"],
                }
            )

    nxt_semester = {
        "title": nxt_sem_title,
        "status": "Not Started",
        "gpa": 0.0,
        "electives": electives,
    }

    semesters.append(nxt_semester)

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

    # Filling the Elective Course Options from users input
    for item in matched_semester.get("courses", []):

        if item.get("code") == "":
            option = next(
                (x for x in payload.electives if x.title == item["title"]), None
            )
            if option:
                item["code"] = option.code
                item["title"] = option.option
                item.pop("choices", None)  # ✅ remove choices if it exists

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
