# AI-Assisted Student University Learning Platform

## Project Overview

The **AI-Assisted Student University Learning Platform** is an intelligent system designed to support students in organizing their academic journey. It offers AI-generated course roadmaps, curated topic-wise resources, and auto-generated quizzes. Built with **FastAPI**, the backend is integrated with **Gemini Studio API** to dynamically extract content based on the course syllabus and user progress.

---

## Backend (FastAPI)

The backend of this platform is built using **FastAPI**, a modern, high-performance Python web framework. The system interacts with the **Gemini Studio API** for various AI-powered features, such as:

- Course roadmap generation from a given syllabus.
- Topic-wise study resources extraction (books, chapters, and websites).
- Quiz question generation for each week's topics.

The Gemini API responses are formatted in **JSON** and parsed through a three-level nested loop before being saved to the database.

---

## Core Features

### AI-Driven Operations
- **Roadmap Generation**: Based on course syllabus and duration input.
- **Topic Resources**: Triggered upon a student opening a topic for the first time.
- **Quiz Questions**: Generated for topics of a given week.

### REST API Endpoints

- `POST /start-semester` – Start a new semester
- `GET /semesters` – Fetch all semesters
- `GET /courses` – Get all courses
- `GET /course-statistics` – View statistics of a course
- `GET /topics` – Retrieve all topics
- `GET /topic-resources/{topic_id}` – Fetch AI-generated resources for a topic
- `POST /start-quiz` – Initiate quiz for a topic/week
- `POST /submit-quiz` – Submit completed quiz
- `GET /academics` – View academic records
- `GET /attendance` – View attendance records
- `PUT /update-marks` – Update marks for a student
- `PUT /update-attendance` – Update attendance for a student
- `PUT /update-topic-status` – Update status of a topic (e.g., started, completed)

---

## Database Configuration

- **Database**: PostgreSQL
- **ORM and Migrations**: Implemented using SQLAlchemy and Alembic.
- All schemas and tables (e.g., Courses, Topics, Users, QuizResults) are created and managed via migrations.

---

## Authentication

A simple **JWT-based authentication** system is implemented for secure access to the APIs. Upon login, a token is issued which must be included in the headers of protected routes.

---

## Tech Stack

- **Backend Framework**: FastAPI
- **AI Integration**: Gemini Studio API
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT Tokens

---

## Frontend Repository

The frontend of this platform is built using React Js and Tailwind CSS and can be found here: [Frontend Repository](https://github.com/Varunkumar0812/AASULP-frontend) <!-- Replace # with actual link -->
