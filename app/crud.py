from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Student, Payment
from app.schemas import StudentCreate, StudentUpdate, PaymentCreate
from app.exceptions import StudentNotFoundError, StudentDeletionBlockedError


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def get_students(db: Session, skip: int = 0, limit: int = 100) -> list[Student]:
    stmt = select(Student).offset(skip).limit(limit).order_by(Student.id)
    return list(db.scalars(stmt).all())


def create_student(db: Session, student_in: StudentCreate) -> Student:
    student = Student(
        name=student_in.name,
        phone=student_in.phone,
        group_name=student_in.group_name,
        monthly_fee=student_in.monthly_fee,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student: Student, student_in: StudentUpdate) -> Student:
    update_data = student_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student: Student) -> None:
    # Deliberate deletion policy: Check if payments exist
    payment_count = db.scalar(
        select(func.count(Payment.id)).where(Payment.student_id == student.id)
    ) or 0

    if payment_count > 0:
        raise StudentDeletionBlockedError(student_id=student.id, payment_count=payment_count)

    db.delete(student)
    db.commit()


def create_payment(db: Session, payment_in: PaymentCreate) -> Payment:
    student = get_student(db, payment_in.student_id)
    if not student:
        raise StudentNotFoundError(student_id=payment_in.student_id)

    payment = Payment(
        student_id=payment_in.student_id,
        amount=payment_in.amount,
        payment_date=payment_in.payment_date,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_student_payments(db: Session, student_id: int) -> list[Payment]:
    student = get_student(db, student_id)
    if not student:
        raise StudentNotFoundError(student_id=student_id)

    stmt = (
        select(Payment)
        .where(Payment.student_id == student_id)
        .order_by(Payment.payment_date.desc(), Payment.id.desc())
    )
    return list(db.scalars(stmt).all())
