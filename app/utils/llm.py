import os
import json
from dotenv import load_dotenv
from google import genai

# Load .env variables
load_dotenv()
client = genai.Client(api_key=os.getenv("AI_API_KEY"))


def getCourseRoadmap(semester, course):
    # A: Read and stringify JSON from file
    with open(
        "C:/Users/tvaru/Desktop/AI-ASULP/app/data/semester_course_details.json", "r"
    ) as f:
        json_data = json.load(f)
    A = json.dumps(json_data, indent=2)  # Pretty-printed for readability

    # B: Placeholder text (you can replace this later)
    B = """
            i am developing application that helps a university student by creating roadmaps for him, each course to help him prepare through out the semester. i have this syllabus for our entire program above. This is how it works, each time a student starts a semester by clicking a button in our semester, you will have the start and end of semester, also the Exams in between. You need to prepare a roadmap for each Course in that Semester, including all the Exams in Between, plan the roadmap has Weeks, within each Weeks there will be many Topics, There is a Quiz after each Week. the Roadmap must be within the Semester Period. Now i will give the database schema for the models in my application i have set.

            Just read it and follow that to create functions.

            User :
            user_id
            first_name - string
            last_name - string
            email - string
            password - string
            cgpa - float

            Semester :
            semester_id
            title - string
            user_id - int
            Courses []
            gpa - float

            Course :
            course_id
            title - string
            code - string
            credit - int
            periods - int
            description - string
            start_date (yyyy-mm-dd) - date
            end_date (yyyy-mm-dd) - date
            type ("Lab", "Theory", "Lab+Theory")
            Exams [] 
            Books []
            Weeks []
            user_id 
            semester_id
            status ("Active", "Completed", "Dropped")
            mark - float
            attendance - float

            Exams :
            exam_id
            title - string
            type  ("Assesment 1", "Assesment 2", "End Semester")
            rank - int
            start date (yyyy-mm-dd) - date
            end date (yyyy-mm-dd) - date
            status ("Scheduled", "Completed")
            mark - float
            user_id
            semester_id

            Weeks :
            week_id
            title - string
            rank - int
            Topics []
            course_id
            quiz_id
            user_id
            status ("Ongoing", "Completed", "Pending")
            attendance - float

            Quiz :
            quiz_id
            title - string
            Questions []
            status ("Pending", "Completed")
            score

            Question :
            question_id
            title - string 
            options - string
            correct ans
            chosen ans
            user_id
            quiz_id

            Topic :
            topic_id
            title - string
            description - string
            resources - string
            status ("Pending", "Completed", "Ongoing")

            Book :
            book_id
            title - string
            author - string
            edition - string
            description - string

            now if a user starts a semester, you need to give me the roadmap for all courses in the semester as a json file, also the weeks, exams in the courses, also the topics in each weeks. The rank attribute in week and exam helps to depict the order in which they will be ordered when combined, the three exams - Assessment I and Assessment II and Final End Semester, the Assessment II and End Semester should be at the final, the Assessment I should be in the middle of the weeks. The rank attribute helps to determine where to place an exam in between weeks, no two weeks or exams can have the same rank.

        """  # Placeholder for B

    # C: Placeholder text (you can replace this later)
    C = f"""
        Just return the roadmap for the course {course} which is in {semester["title"]} and the semester lies between the period semester start data : {semester["start_date"]} and end date : {semester["end_date"]}, I clearly only want a json data, no other extra texts content should be present, just json data that depicts the roadmap for the course i gave
    """

    # Final prompt = A + B + C
    prompt = A + B + C

    # Call Gemini
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)

    try:
        return json.loads(
            response.text.strip().removeprefix("```json").removesuffix("```").strip()
        )
    except json.JSONDecodeError:
        print("Could not parse JSON. Raw response:")
        print(response.text)
        return {}


# Example usage:
# roadmap = getCourseRoadmap()
# print(roadmap)
