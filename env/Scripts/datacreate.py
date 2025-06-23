from faker import Faker
import random

faker = Faker()

class Student:
    def __init__(self,student_id):
        self.student_id =student_id
        self.name = faker.name()
        self.age = random.randint(18,25)
        self.email = faker.email()
        self.gender = random.choice(["Male","Female","Other"])
        self.phone = faker.phone_number()
        self.enrollment_year = random.randint(2022,2025)
        self.course_batch = random.choice(["Data Science", "Web Development", "Cyber Security", "AI and ML"])
        self.city = faker.city()
        self.graduation_year = self.enrollment_year + 2

class Programming:
    def __init__(self,student_id):
        self.student_id = student_id
        self.language = random.choice(["Python", "Java", "C++", "JavaScript"])
        self.problems_solved = random.randint(0, 200)
        self.assessments_completed = random.randint(0, 10)
        self.mini_project = random.randint(0,5)
        self.certifications_earned = random.randint(0, 5)
        self.latest_project_score = random.randint(40, 100)

class soft_skills:
    def __init__(self,student_id):
        self.student_id = student_id
        self.communication= random.randint(0, 100)
        self.teamwork = random.randint(0, 100)
        self.presentation = random.randint(0, 100)
        self.leadership = random.randint(0, 100)
        self.critical_thinking = random.randint(0, 100)
        self.interpersonal_skills = random.randint(0, 100)

class Placement:
    def __init__(self,student_id):
        self.student_id = student_id
        self.mock_interviews = random.randint(0, 100)
        self.internships = random.randint(0, 10)
        self.placement_status = random.choice(["Placed", "Not Ready","Ready"])
        self.company_name = faker.company() if self.placement_status == "Placed" else None
        self.placement_package = random.randint(100000,700000) if self.placement_status =="Placed" else None
        self.interview_rounds_cleared = random.randint(0,5)
        self.placement_date = faker.date_time_this_year() if self.placement_status =="Placed" else None


