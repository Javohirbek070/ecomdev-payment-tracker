import datetime
from decimal import Decimal
from sqlalchemy import (
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2, asdecimal=True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Deliberate deletion policy: Restrict deletion when payments exist to ensure accounting integrity
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="student",
        cascade="",  # Do not cascade delete
        passive_deletes=False,
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}', group='{self.group_name}')>"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2, asdecimal=True), nullable=False)
    payment_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student: Mapped["Student"] = relationship("Student", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, student_id={self.student_id}, amount={self.amount}, date={self.payment_date})>"
