from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Enforce foreign key constraints in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides an independent SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine=None) -> None:
    """Create all database tables if they do not exist."""
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)


def seed_initial_data_if_empty(session: Session) -> None:
    """Seed sample educational center students and payments if database is empty."""
    from app.models import Student, Payment
    import datetime
    from decimal import Decimal

    student_count = session.query(Student).count()
    if student_count > 0:
        return

    today = datetime.date.today()
    cur_year = today.year
    cur_month = today.month

    s1 = Student(name="Ali Valiyev", phone="+998901234567", group_name="Python Backend", monthly_fee=Decimal("800000.00"))
    s2 = Student(name="Sardor Rahimov", phone="+998912345678", group_name="Frontend React", monthly_fee=Decimal("750000.00"))
    s3 = Student(name="Malika Karimova", phone="+998933456789", group_name="IELTS 7.0", monthly_fee=Decimal("900000.00"))
    s4 = Student(name="Jasur Bekmurodov", phone="+998944567890", group_name="Python Backend", monthly_fee=Decimal("800000.00"))
    s5 = Student(name="Dilnoza Alimova", phone="+998975678901", group_name="Data Science", monthly_fee=Decimal("850000.00"))

    session.add_all([s1, s2, s3, s4, s5])
    session.commit()

    # Add realistic payments in the current calendar month
    p1 = Payment(student_id=s1.id, amount=Decimal("800000.00"), payment_date=datetime.date(cur_year, cur_month, 5))
    p2 = Payment(student_id=s2.id, amount=Decimal("400000.00"), payment_date=datetime.date(cur_year, cur_month, 10))
    p3 = Payment(student_id=s4.id, amount=Decimal("500000.00"), payment_date=datetime.date(cur_year, cur_month, 12))
    p4 = Payment(student_id=s5.id, amount=Decimal("850000.00"), payment_date=datetime.date(cur_year, cur_month, 8))

    session.add_all([p1, p2, p3, p4])
    session.commit()
