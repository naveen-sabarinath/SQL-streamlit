from Scripts.datacreate import Student, Programming, soft_skills, Placement
from Scripts.db_util import get_connection, execute_query
import os

NUM_STUDENTS = 100  # Number of students to generate
conn = get_connection()

for student_id in range(1, NUM_STUDENTS + 1):
    student = Student(student_id)
    programming = Programming(student_id)
    soft_skill = soft_skills(student_id)
    placement = Placement(student_id)

    # Insert into students table
    execute_query(conn, """
        INSERT INTO students (student_id, name, age, gender, email, phone,
                              enrollment_year, course_batch, city, graduation_year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (student.student_id, student.name, student.age, student.gender,
          student.email, student.phone, student.enrollment_year,
          student.course_batch, student.city, student.graduation_year))
    execute_query(conn, """
        INSERT INTO programming (student_id, language, problems_solved, assessments_completed,
                                 mini_projects, certifications_earned, latest_project_score)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (programming.student_id, programming.language, programming.problems_solved,
          programming.assessments_completed, programming.mini_project,
          programming.certifications_earned, programming.latest_project_score))
    execute_query(conn, """
        INSERT INTO softskills (student_id, communication, teamwork, presentation,
                                leadership, critical_thinking, interpersonal_skills)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (soft_skill.student_id, soft_skill.communication, soft_skill.teamwork, soft_skill.presentation,
          soft_skill.leadership, soft_skill.critical_thinking, soft_skill.interpersonal_skills))
    execute_query(conn, """
        INSERT INTO placements (student_id, mock_interview_score, internships_completed,
                                placement_status, company_name, placement_package,
                                interview_rounds_cleared, placement_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (placement.student_id, placement.mock_interviews, placement.internships,
          placement.placement_status, placement.company_name, placement.placement_package,
          placement.interview_rounds_cleared, placement.placement_date))
conn.close()
print("Data inserted successfully.")
