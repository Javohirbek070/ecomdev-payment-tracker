class AppError(Exception):
    """Base exception for application errors."""
    pass


class StudentNotFoundError(AppError):
    def __init__(self, student_id: int):
        super().__init__(f"Student with id {student_id} not found")
        self.student_id = student_id


class StudentDeletionBlockedError(AppError):
    def __init__(self, student_id: int, payment_count: int):
        super().__init__(
            f"Cannot delete student with id {student_id}: {payment_count} payment record(s) exist. "
            "Deletion is restricted to preserve financial and accounting integrity."
        )
        self.student_id = student_id
        self.payment_count = payment_count


class InvalidMonthFormatError(AppError):
    def __init__(self, month_str: str):
        super().__init__(
            f"Invalid month format: '{month_str}'. Expected format is YYYY-MM (e.g., 2026-10)."
        )
        self.month_str = month_str
