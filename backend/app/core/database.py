"""
SQLAlchemy engine/session setup.

Uses SQLite for local development but is structured (via SQLAlchemy's
dialect-agnostic ORM + DATABASE_URL) so switching to PostgreSQL later is
just a matter of changing DATABASE_URL and installing psycopg2.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Import all models before calling this."""
    from app.models import user, employee, course, learning_record, certificate, enrollment, setting  # noqa: F401
    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "sqlite":
        columns = {column["name"] for column in inspect(engine).get_columns("courses")}
        additions = []
        if "price" not in columns:
            additions.append("ALTER TABLE courses ADD COLUMN price FLOAT NOT NULL DEFAULT 0")
        if "videos" not in columns:
            additions.append("ALTER TABLE courses ADD COLUMN videos JSON NOT NULL DEFAULT '[]'")
        if additions:
            with engine.begin() as connection:
                for statement in additions:
                    connection.execute(text(statement))
        certificate_columns = {column["name"] for column in inspect(engine).get_columns("certificates")}
        if "course_id" not in certificate_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE certificates ADD COLUMN course_id INTEGER"))
        enrollment_columns = {column["name"] for column in inspect(engine).get_columns("enrollments")}
        if "watched_video_ids" not in enrollment_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE enrollments ADD COLUMN watched_video_ids JSON NOT NULL DEFAULT '[]'"))
