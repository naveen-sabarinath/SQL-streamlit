from Scripts.datacreate import Student, Programming, soft_skills, Placement
from Scripts.db_util import get_connection, execute_query
import os


os.makedirs("data",exist_ok=True)

conn = get_connection()

# 1. Create Tables
create_students = """
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT, age INTEGER, gender TEXT, email TEXT,
    phone TEXT, enrollment_year INTEGER, course_batch TEXT,
    city TEXT, graduation_year INTEGER
);
"""

create_programming = """
CREATE TABLE IF NOT EXISTS programming (
    programming_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER, language TEXT, problems_solved INTEGER,
    assessments_completed INTEGER, mini_projects INTEGER,
    certifications_earned INTEGER, latest_project_score INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
);
"""

create_softskills = """
CREATE TABLE IF NOT EXISTS softskills (
    soft_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    communication INTEGER, teamwork INTEGER, presentation INTEGER,
    leadership INTEGER, critical_thinking INTEGER, interpersonal_skills INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
);
"""

create_placements = """
CREATE TABLE IF NOT EXISTS placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    mock_interview_score INTEGER, internships_completed INTEGER,
    placement_status TEXT, company_name TEXT, placement_package INTEGER,
    interview_rounds_cleared INTEGER, placement_date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
);
"""

for query in [create_students, create_programming, create_softskills, create_placements]:
    execute_query(conn, query)

conn.close()
print("Tables created successfully.")
