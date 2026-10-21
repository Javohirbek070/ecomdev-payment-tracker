from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MonthlyDebtorsResponse
from app.services.debtors import get_monthly_debtors
from app.exceptions import InvalidMonthFormatError

router = APIRouter(prefix="/debtors", tags=["Debtors"])


@router.get("", response_model=MonthlyDebtorsResponse, status_code=status.HTTP_200_OK)
def list_debtors(
    month: str = Query(
        ...,
        description="Target calendar month in YYYY-MM format (e.g., 2026-10)",
        examples=["2026-10"],
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve students who have outstanding debt for the specified calendar month.
    
    A student is considered a debtor if their total payments with payment_date
    in the specified month are less than their current monthly fee.
    """
    try:
        return get_monthly_debtors(db, month_str=month)
    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
