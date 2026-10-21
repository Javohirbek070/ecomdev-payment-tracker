from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import PaymentCreate, PaymentResponse
from app import crud
from app.exceptions import StudentNotFoundError

router = APIRouter(tags=["Payments"])


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
