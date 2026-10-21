import datetime
from decimal import Decimal
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_validator


def _validate_non_empty_str(field_name: str, value: Optional[str]) -> Optional[str]:
    if value is not None:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError(f"{field_name} cannot be empty or whitespace only.")
        return trimmed
    return value


def _serialize_decimal(v: Decimal) -> float:
    return float(v)


MoneyDecimal = Annotated[
    Decimal,
    PlainSerializer(_serialize_decimal, return_type=float, when_used="json-unless-none"),
]


# --- Student Schemas ---

class StudentBase(BaseModel):
    name: str = Field(..., description="Full name of the student")
    phone: str = Field(..., description="Contact phone number")
    group_name: str = Field(..., description="Enrolled group name")
    monthly_fee: MoneyDecimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Monthly tuition fee (must be positive exact monetary value)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_non_empty_str("name", v)  # type: ignore

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_non_empty_str("phone", v)  # type: ignore

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, v: str) -> str:
        return _validate_non_empty_str("group_name", v)  # type: ignore


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the student")
    phone: Optional[str] = Field(None, description="Contact phone number")
    group_name: Optional[str] = Field(None, description="Enrolled group name")
    monthly_fee: Optional[MoneyDecimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Monthly tuition fee (must be positive exact monetary value)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return _validate_non_empty_str("name", v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return _validate_non_empty_str("phone", v)

    @field_validator("group_name")
    @classmethod
    def validate_group_name(cls, v: Optional[str]) -> Optional[str]:
        return _validate_non_empty_str("group_name", v)


class StudentResponse(StudentBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# --- Payment Schemas ---

class PaymentCreate(BaseModel):
    student_id: int = Field(..., gt=0, description="ID of the student")
    amount: MoneyDecimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Payment amount (must be positive exact monetary value)",
    )
    payment_date: datetime.date = Field(..., description="Date of the payment (YYYY-MM-DD)")


class PaymentResponse(BaseModel):
    id: int
    student_id: int
    amount: MoneyDecimal
    payment_date: datetime.date
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# --- Debtor Schemas ---

class DebtorItem(BaseModel):
    student_id: int
    name: str
    phone: str
    group_name: str
    monthly_fee: MoneyDecimal
    total_paid: MoneyDecimal
    debt: MoneyDecimal

    model_config = ConfigDict(from_attributes=True)


class MonthlyDebtorsResponse(BaseModel):
    month: str
    debtors: list[DebtorItem]
