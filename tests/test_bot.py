import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot.main import handle_start, handle_debt, handle_pay, is_user_authorized
from app.models import Student, Payment
from app.config import settings


@pytest.mark.asyncio
async def test_bot_authorization():
    """Verify authorization logic for admin user IDs."""
    with patch.object(settings, "telegram_admin_ids", [12345, 67890]):
        assert is_user_authorized(12345) is True
        assert is_user_authorized(67890) is True
        assert is_user_authorized(99999) is False

    with patch.object(settings, "telegram_admin_ids", []):
        assert is_user_authorized(12345) is False


@pytest.mark.asyncio
async def test_bot_start_command():
    """Verify /start command sends welcome message."""
    mock_message = AsyncMock()
    await handle_start(mock_message)
    mock_message.answer.assert_called_once()
    assert "Welcome to Learning Center Payment Tracker Bot" in mock_message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_bot_pay_unauthorized():
    """Verify /pay command rejects unauthorized users."""
    mock_message = AsyncMock()
    mock_message.from_user.id = 99999  # unauthorized user
    mock_message.text = "/pay 1 100000"

    with patch.object(settings, "telegram_admin_ids", [12345]):
        await handle_pay(mock_message)

    mock_message.answer.assert_called_once()
    assert "Access Denied" in mock_message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_bot_pay_invalid_arguments():
    """Verify /pay command validates arguments properly."""
    admin_id = 12345

    with patch.object(settings, "telegram_admin_ids", [admin_id]):
        # Missing amount
        mock_msg1 = AsyncMock()
        mock_msg1.from_user.id = admin_id
        mock_msg1.text = "/pay 1"
        await handle_pay(mock_msg1)
        assert "Invalid arguments" in mock_msg1.answer.call_args[0][0]

        # Invalid student ID (non-integer)
        mock_msg2 = AsyncMock()
        mock_msg2.from_user.id = admin_id
        mock_msg2.text = "/pay abc 50000"
        await handle_pay(mock_msg2)
        assert "Invalid student ID" in mock_msg2.answer.call_args[0][0]

        # Nonpositive amount
        mock_msg3 = AsyncMock()
        mock_msg3.from_user.id = admin_id
        mock_msg3.text = "/pay 1 -50000"
        await handle_pay(mock_msg3)
        assert "Invalid amount" in mock_msg3.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_bot_pay_and_debt_with_db(db_session):
    """Verify bot /pay and /debt commands interact with database correctly."""
    admin_id = 12345

    # Create student in DB
    student = Student(
        name="Bot Test Student",
        phone="+998901112233",
        group_name="Python",
        monthly_fee=500000.0,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    # Patch SessionLocal to return db_session
    mock_session_maker = MagicMock()
    mock_session_maker.return_value.__enter__.return_value = db_session
    mock_session_maker.return_value.__exit__.return_value = None

    with patch("bot.main.SessionLocal", mock_session_maker), \
         patch.object(settings, "telegram_admin_ids", [admin_id]):

        # 1. Pay for nonexistent student
        mock_msg_nonexistent = AsyncMock()
        mock_msg_nonexistent.from_user.id = admin_id
        mock_msg_nonexistent.text = "/pay 99999 200000"
        await handle_pay(mock_msg_nonexistent)
        assert "Student not found" in mock_msg_nonexistent.answer.call_args[0][0]

        # 2. Record successful payment
        mock_msg_pay = AsyncMock()
        mock_msg_pay.from_user.id = admin_id
        mock_msg_pay.text = f"/pay {student.id} 200000"
        await handle_pay(mock_msg_pay)
        assert "Payment successfully recorded" in mock_msg_pay.answer.call_args[0][0]

        # Check DB payment
        payment = db_session.query(Payment).filter(Payment.student_id == student.id).first()
        assert payment is not None
        assert payment.amount == 200000.0

        # 3. Check /debt command
        mock_msg_debt = AsyncMock()
        await handle_debt(mock_msg_debt)
        assert "Debtors for" in mock_msg_debt.answer.call_args[0][0]
        assert "Remaining Debt: 300,000.00" in mock_msg_debt.answer.call_args[0][0]
