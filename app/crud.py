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


def get_all_payments(db: Session, skip: int = 0, limit: int = 50) -> list[dict]:
    stmt = (
        select(
            Payment,
            Student.name.label("student_name"),
            Student.group_name.label("group_name"),
        )
        .join(Student, Payment.student_id == Student.id)
        .order_by(Payment.payment_date.desc(), Payment.id.desc())
        .offset(skip)
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    results = []
    for payment, student_name, group_name in rows:
        results.append({
            "id": payment.id,
            "student_id": payment.student_id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "created_at": payment.created_at,
            "student_name": student_name,
            "group_name": group_name,
        })
    return results
