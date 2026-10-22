from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PaymentCreate, PaymentResponse, PaymentWithStudentResponse
from app import crud
from app.exceptions import StudentNotFoundError

router = APIRouter(tags=["Payments"])


@router.get(
    "/payments",
    response_model=list[PaymentWithStudentResponse],
    status_code=status.HTTP_200_OK,
)
def list_all_payments(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=500, description="Limit records"),
    db: Session = Depends(get_db),
):
    """List recent tuition payments with student information."""
    return crud.get_all_payments(db, skip=skip, limit=limit)


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_in: PaymentCreate, db: Session = Depends(get_db)):
    """Record a tuition payment for an existing student."""
    try:
        return crud.create_payment(db, payment_in)
    except StudentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/students/{student_id}/payments",
    response_model=list[PaymentResponse],
    status_code=status.HTTP_200_OK,
)
def list_student_payments(student_id: int, db: Session = Depends(get_db)):
    """List payment history for a specific student."""
    try:
        return crud.get_student_payments(db, student_id)
    except StudentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
