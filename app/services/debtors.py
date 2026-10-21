import calendar
import datetime
import re
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models import Student, Payment
from app.schemas import DebtorItem, MonthlyDebtorsResponse
from app.exceptions import InvalidMonthFormatError

MONTH_REGEX = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


def parse_month_bounds(month_str: str) -> tuple[datetime.date, datetime.date]:
    """
    Validate and parse a YYYY-MM string into the start and end dates of the calendar month.
    
    Raises:
        InvalidMonthFormatError: If the month format is invalid or out of calendar range.
    """
    match = MONTH_REGEX.match(month_str.strip() if month_str else "")
    if not match:
        raise InvalidMonthFormatError(month_str)

    year = int(match.group(1))
    month = int(match.group(2))

    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, last_day)
    return start_date, end_date


def get_monthly_debtors(db: Session, month_str: str) -> MonthlyDebtorsResponse:
    """
    Calculate and return debtors for the specified calendar month.
    
    Accounting Rule:
        - Debt is calculated against the student's current monthly fee.
        - All payments whose `payment_date` falls between the first and last calendar day
          (inclusive) of the target month are aggregated.
        - Students whose total paid amount is less than their current monthly fee are included.
        - Students who have paid in full (total_paid >= monthly_fee) or overpaid are excluded.
        - If a student made no payments in the month, total_paid is 0.0 and debt equals monthly_fee.
    """
    start_date, end_date = parse_month_bounds(month_str)

    # Database aggregation query:
    # Outer join students with payments made within the requested month range,
    # grouping by student to calculate the sum of payments.
    stmt = (
        select(
            Student,
            func.coalesce(func.sum(Payment.amount), 0.0).label("total_paid"),
        )
        .outerjoin(
            Payment,
            and_(
                Payment.student_id == Student.id,
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date,
            ),
        )
        .group_by(Student.id)
        .order_by(Student.id)
    )

    rows = db.execute(stmt).all()

    debtors: list[DebtorItem] = []
    for student, total_paid_raw in rows:
        total_paid = round(float(total_paid_raw or 0.0), 2)
        monthly_fee = round(float(student.monthly_fee), 2)

        # Include only students whose total payment is lower than their monthly fee
        if total_paid < monthly_fee:
            debt = round(monthly_fee - total_paid, 2)
            debtors.append(
                DebtorItem(
                    student_id=student.id,
                    name=student.name,
                    phone=student.phone,
                    group_name=student.group_name,
                    monthly_fee=monthly_fee,
                    total_paid=total_paid,
                    debt=debt,
                )
            )

    return MonthlyDebtorsResponse(month=month_str, debtors=debtors)
