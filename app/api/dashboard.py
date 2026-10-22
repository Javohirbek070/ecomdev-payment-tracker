import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Student, Payment
from app.schemas import DashboardSummaryResponse
from app.services.debtors import get_monthly_debtors, parse_month_bounds
from app.exceptions import InvalidMonthFormatError
from app import crud

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse, status_code=status.HTTP_200_OK)
def get_dashboard_summary(
    month: str | None = Query(
        None,
        description="Target calendar month in YYYY-MM format. Defaults to current month.",
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve aggregated dashboard statistics for an educational center.
    Calculates student counts, expected vs actual revenue, outstanding debt, and recent payments.
    """
    if not month:
        now = datetime.date.today()
        month = now.strftime("%Y-%m")

    try:
        start_date, end_date = parse_month_bounds(month)
    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    two_places = Decimal("0.01")

    # 1. Total number of students
    total_students = db.scalar(select(func.count(Student.id))) or 0

    # 2. Total expected monthly tuition (sum of all active students' monthly fees)
    total_expected_raw = db.scalar(select(func.coalesce(func.sum(Student.monthly_fee), 0))) or 0
    total_expected_tuition = Decimal(str(total_expected_raw)).quantize(two_places)

    # 3. Total collected this month (sum of payments with payment_date in target month)
    total_collected_raw = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
        )
    ) or 0
    total_collected = Decimal(str(total_collected_raw)).quantize(two_places)

    # 4. Debtors and total outstanding debt
    debtors_resp = get_monthly_debtors(db, month_str=month)
    total_debt = sum((d.debt for d in debtors_resp.debtors), Decimal("0.00")).quantize(two_places)
    debtors_count = len(debtors_resp.debtors)

    # 5. Recent payments
    recent_payments = crud.get_all_payments(db, skip=0, limit=10)

    return DashboardSummaryResponse(
        month=month,
        total_students=total_students,
        total_expected_tuition=total_expected_tuition,
        total_collected=total_collected,
        total_debt=total_debt,
        debtors_count=debtors_count,
        recent_payments=recent_payments,
    )
