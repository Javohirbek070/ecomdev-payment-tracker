from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app import crud
from app.exceptions import StudentDeletionBlockedError

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student record."""
    return crud.create_student(db, student_in)


@router.get("", response_model=list[StudentResponse], status_code=status.HTTP_200_OK)
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered students with pagination."""
    return crud.get_students(db, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific student by ID."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    return student


@router.patch("/{student_id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
def update_student(student_id: int, student_in: StudentUpdate, db: Session = Depends(get_db)):
    """Update details for an existing student."""
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )
    return crud.update_student(db, student, student_in)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Delete a student record.
    
    Deletion Policy:
    Deletion is prevented with an HTTP 400 Bad Request error if the student has
    existing payment records, preserving financial and accounting integrity.
    """
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found",
        )

    try:
        crud.delete_student(db, student)
    except StudentDeletionBlockedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
