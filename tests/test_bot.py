import datetime
from decimal import Decimal
import pytest
import httpx
from unittest.mock import AsyncMock, patch

from bot.main import handle_start, handle_debt, handle_pay, is_user_authorized
from app.config import settings
from app.main import app


@pytest.mark.asyncio
async def test_bot_authorization():
    """Verify authorization logic for admin user IDs."""
    with patch.object(settings, "telegram_admin_ids", [12345, 67890]):
        assert is_user_authorized(12345) is True
        assert is_user_authorized(67890) is True
        assert is_user_authorized(99999) is False
        assert is_user_authorized(None) is False

    with patch.object(settings, "telegram_admin_ids", []):
        assert is_user_authorized(12345) is False
        assert is_user_authorized(None) is False


@pytest.mark.asyncio
async def test_bot_start_command():
    """Verify /start command sends welcome message and instructions."""
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
async def test_bot_pay_and_debt_with_httpx(client):
    """
    Verify bot /pay and /debt commands communicate with the FastAPI service
    over HTTPX and handle responses properly.
    """
    admin_id = 12345

    # Create a student via the test client
    student_res = client.post(
        "/students",
        json={
            "name": "Bot HTTP Student",
            "phone": "+998901112233",
            "group_name": "Python",
            "monthly_fee": 500000.0,
        },
    )
    assert student_res.status_code == 201
    student = student_res.json()

    # Use ASGITransport to communicate directly with FastAPI app over HTTP
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as http_client:

        with patch.object(settings, "telegram_admin_ids", [admin_id]), \
             patch.object(settings, "api_base_url", "http://testserver"):

            # 1. Pay for nonexistent student
            mock_msg_nonexistent = AsyncMock()
            mock_msg_nonexistent.from_user.id = admin_id
            mock_msg_nonexistent.text = "/pay 99999 200000"
            await handle_pay(mock_msg_nonexistent, client=http_client)
            assert "Student not found" in mock_msg_nonexistent.answer.call_args[0][0]

            # 2. Record successful payment
            mock_msg_pay = AsyncMock()
            mock_msg_pay.from_user.id = admin_id
            mock_msg_pay.text = f"/pay {student['id']} 200000"
            await handle_pay(mock_msg_pay, client=http_client)
            assert "Payment successfully recorded" in mock_msg_pay.answer.call_args[0][0]

            # 3. Check /debt command
            mock_msg_debt = AsyncMock()
            await handle_debt(mock_msg_debt, client=http_client)
            assert "Debtors for" in mock_msg_debt.answer.call_args[0][0]
            assert "Remaining Debt: 300,000.00" in mock_msg_debt.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_bot_handles_network_error():
    """Verify bot safely handles network or server connection failures without stack traces."""
    admin_id = 12345

    # Mock an HTTP client that raises a connection error
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("Connection refused")
    mock_client.post.side_effect = httpx.ConnectError("Connection refused")

    with patch.object(settings, "telegram_admin_ids", [admin_id]), \
         patch.object(settings, "api_base_url", "http://unavailable-server:9999"):

        # Test /debt failure
        msg_debt = AsyncMock()
        await handle_debt(msg_debt, client=mock_client)
        assert "Failed to communicate with the payment server" in msg_debt.answer.call_args[0][0]

        # Test /pay failure
        msg_pay = AsyncMock()
        msg_pay.from_user.id = admin_id
        msg_pay.text = "/pay 1 100000"
        await handle_pay(msg_pay, client=mock_client)
        assert "Failed to communicate with the payment server" in msg_pay.answer.call_args[0][0]
