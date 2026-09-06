"""
Seed script - populates the database with realistic demo data.

Run with:  python -m app.seed

Creates:
  - 1 admin
  - 5 employees (with target/achieved hours matching the spec, so the
    dashboard demonstrates eligible, non-eligible, and different targets)
  - 8 courses
  - learning records that sum to each employee's target achieved hours
"""
import logging
from datetime import date

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.employee import Employee, EmployeeStatus
from app.models.course import Course
from app.models.learning_record import LearningRecord, LearningStatus
from app.services.learning_calc import recalculate_employee_hours
from app.services import settings_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.seed")

COURSES = [
    ("CRS-001", "Python Fundamentals", "Programming", 10, 0),
    ("CRS-002", "Data Analysis with Python", "Programming", 15, 0),
    ("CRS-003", "Effective Communication", "Soft Skills", 8, 0),
    ("CRS-004", "Leadership Essentials", "Management", 12, 0),
    ("CRS-005", "Cloud Computing Basics", "Technology", 20, 39.99),
    ("CRS-006", "Project Management Fundamentals", "Management", 18, 29.99),
    ("CRS-007", "Cybersecurity Awareness", "Technology", 6, 0),
    ("CRS-008", "Advanced Excel", "Productivity", 10, 14.99),
]

COURSE_VIDEOS = {
    "CRS-001": [{"id": "python-basics", "title": "Python for Beginners", "youtube_id": "rfscVS0vtbw", "duration": "4:26:52"}],
    "CRS-002": [{"id": "pandas-data", "title": "Data Analysis with Pandas", "youtube_id": "vmEHCJofslg", "duration": "1:08:48"}],
    "CRS-003": [{"id": "communication", "title": "Communication Skills", "youtube_id": "HAnw168huqA", "duration": "11:42"}],
    "CRS-004": [{"id": "leadership", "title": "Leadership Skills", "youtube_id": "NGxdFMnEjHI", "duration": "12:34"}],
    "CRS-005": [{"id": "cloud-basics", "title": "Cloud Computing Explained", "youtube_id": "M988_fsOSWo", "duration": "15:42"}],
    "CRS-006": [{"id": "project-management", "title": "Project Management Fundamentals", "youtube_id": "ThDdHETxA-g", "duration": "9:58"}],
    "CRS-007": [{"id": "cybersecurity", "title": "Cybersecurity Essentials", "youtube_id": "inWWhr5tnEA", "duration": "14:36"}],
    "CRS-008": [{"id": "excel", "title": "Excel for Beginners", "youtube_id": "Vl0H-qTclOg", "duration": "1:09:12"}],
}

QUIZ_TOPICS = {
    "CRS-001": ("Python Fundamentals", "writing readable Python code", "functions and variables"),
    "CRS-002": ("Data Analysis with Python", "cleaning and interpreting datasets", "pandas DataFrames"),
    "CRS-003": ("Effective Communication", "clear and active communication", "active listening"),
    "CRS-004": ("Leadership Essentials", "guiding a team toward shared goals", "constructive feedback"),
    "CRS-005": ("Cloud Computing Basics", "using scalable cloud resources", "virtual machines"),
    "CRS-006": ("Project Management Fundamentals", "planning and delivering project work", "a project schedule"),
    "CRS-007": ("Cybersecurity Awareness", "protecting systems and information", "multi-factor authentication"),
    "CRS-008": ("Advanced Excel", "analyzing and presenting spreadsheet data", "pivot tables"),
}


def quiz_questions_for(course_code):
    title, focus, example = QUIZ_TOPICS[course_code]
    return [
        {"id": "q1", "question": f"What is a primary focus of {title}?", "options": [focus, "Avoiding all practice", "Removing useful data", "Skipping the lessons"], "correct_option": focus},
        {"id": "q2", "question": f"Which topic is most relevant to {title}?", "options": [example, "Unrelated paperwork", "Random guessing", "Ignoring results"], "correct_option": example},
        {"id": "q3", "question": f"What is the best way to improve in {title}?", "options": ["Practice the course skills", "Never review mistakes", "Skip every exercise", "Avoid applying concepts"], "correct_option": "Practice the course skills"},
        {"id": "q4", "question": f"What should learners do when applying {title}?", "options": ["Use the concepts in a realistic task", "Ignore the requirements", "Choose answers at random", "Avoid checking the outcome"], "correct_option": "Use the concepts in a realistic task"},
        {"id": "q5", "question": "What score is needed to unlock the certificate?", "options": ["80%", "20%", "50%", "Any score"], "correct_option": "80%"},
    ]

def build_learning_plan():
    """
    Explicit learning-record plans per employee so the totals match the
    spec exactly:
      Employee 1 = 52 hours, target 50
      Employee 2 = 68 hours, target 50
      Employee 3 = 32 hours, target 50
      Employee 4 = 45 hours, target 50
      Employee 5 = 75 hours, target 60
    """
    return {
        "EMP-001": [  # Rahul Sharma -> 52 hours (target 50, ELIGIBLE)
            ("CRS-001", 10, 100),
            ("CRS-002", 15, 100),
            ("CRS-004", 12, 100),
            ("CRS-007", 6, 100),
            ("CRS-003", 9, 100),  # partial hours of an 8h course rounded via completion pct; use 9 explicitly
        ],
        "EMP-002": [  # Priya Nair -> 68 hours (target 50, ELIGIBLE)
            ("CRS-001", 10, 100),
            ("CRS-002", 15, 100),
            ("CRS-005", 20, 100),
            ("CRS-006", 18, 100),
            ("CRS-007", 5, 80),
        ],
        "EMP-003": [  # Arjun Mehta -> 32 hours (target 50, NOT eligible)
            ("CRS-001", 10, 100),
            ("CRS-003", 8, 100),
            ("CRS-007", 6, 100),
            ("CRS-008", 8, 80),
        ],
        "EMP-004": [  # Sneha Iyer -> 45 hours (target 50, NOT eligible)
            ("CRS-002", 15, 100),
            ("CRS-004", 12, 100),
            ("CRS-006", 18, 90),
        ],
        "EMP-005": [  # Vikram Rao -> 75 hours (target 60, ELIGIBLE)
            ("CRS-005", 20, 100),
            ("CRS-006", 18, 100),
            ("CRS-002", 15, 100),
            ("CRS-004", 12, 100),
            ("CRS-007", 6, 100),
            ("CRS-008", 4, 40),
        ],
    }


EMPLOYEE_INFO = [
    ("EMP-001", "Rahul Sharma", "rahul.sharma@example.com", "Engineering", "Software Engineer", 50),
    ("EMP-002", "Priya Nair", "priya.nair@example.com", "Marketing", "Marketing Specialist", 50),
    ("EMP-003", "Arjun Mehta", "arjun.mehta@example.com", "Sales", "Sales Executive", 50),
    ("EMP-004", "Sneha Iyer", "sneha.iyer@example.com", "HR", "HR Coordinator", 50),
    ("EMP-005", "Vikram Rao", "vikram.rao@example.com", "Engineering", "Senior Software Engineer", 60),
]

DEMO_PASSWORD = "Password123!"


def seed():
    init_db()
    db = SessionLocal()

    try:
        settings_service.ensure_defaults(db)

        if db.query(User).filter(User.email == "admin@example.com").first():
            seeded_prices = {code: price for code, _, _, _, price in COURSES}
            for course in db.query(Course).all():
                if course.course_code in seeded_prices:
                    course.price = seeded_prices[course.course_code]
                    course.videos = COURSE_VIDEOS.get(course.course_code, [])
                    course.payment_mode = "online" if course.price > 0 else "not_required"
                    course.quiz_questions = quiz_questions_for(course.course_code)
            db.commit()
            logger.info("Seed data already present - skipping seed.")
            return

        # --- Admin ---
        admin = User(
            email="admin@example.com",
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Created admin user: admin@example.com / %s", DEMO_PASSWORD)

        # --- Courses ---
        course_map = {}
        for code, title, category, duration, price in COURSES:
            course = Course(course_code=code, title=title, category=category, duration_hours=duration, price=price, payment_mode="online" if price > 0 else "not_required", videos=COURSE_VIDEOS.get(code, []), quiz_questions=quiz_questions_for(code))
            db.add(course)
            db.commit()
            db.refresh(course)
            course_map[code] = course
        logger.info("Created %d courses", len(COURSES))

        # --- Employees + users ---
        employee_map = {}
        for code, name, email, dept, designation, target in EMPLOYEE_INFO:
            employee = Employee(
                employee_code=code,
                full_name=name,
                email=email,
                department=dept,
                designation=designation,
                joining_date=date(2024, 1, 15),
                target_hours=target,
                total_learning_hours=0,
                status=EmployeeStatus.ACTIVE,
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
            employee_map[code] = employee

            user = User(
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                role=UserRole.EMPLOYEE,
                employee_id=employee.id,
                is_active=True,
            )
            db.add(user)
            db.commit()
        logger.info("Created %d employees + user accounts", len(EMPLOYEE_INFO))

        # --- Learning records ---
        plan = build_learning_plan()
        for emp_code, records in plan.items():
            employee = employee_map[emp_code]
            for course_code, hours, pct in records:
                course = course_map[course_code]
                record = LearningRecord(
                    employee_id=employee.id,
                    course_id=course.id,
                    learning_hours=hours,
                    completion_percentage=pct,
                    completion_date=date(2024, 6, 1),
                    status=LearningStatus.COMPLETED if pct >= 100 else LearningStatus.IN_PROGRESS,
                )
                db.add(record)
            db.commit()
            total = recalculate_employee_hours(db, employee.id)
            logger.info("%s (%s): total_learning_hours=%.1f target=%.1f", employee.full_name, emp_code, total, employee.target_hours)

        logger.info("Seed complete.")
        logger.info("Demo credentials -> Admin: admin@example.com / %s", DEMO_PASSWORD)
        for code, name, email, *_ in EMPLOYEE_INFO:
            logger.info("Demo credentials -> Employee (%s): %s / %s", name, email, DEMO_PASSWORD)

    finally:
        db.close()


if __name__ == "__main__":
    seed()
