import asyncio
import datetime
import logging
import sys
from decimal import Decimal, InvalidOperation
from typing import Optional

import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram_bot")

dp = Dispatcher()


def is_user_authorized(user_id: Optional[int], username: Optional[str] = None) -> bool:
    """
    Check if the user is authorized to perform financial actions.
    Authorizes if either:
    1. The user's numeric Telegram User ID is in settings.telegram_admin_ids.
    2. The user's Telegram username (e.g. @code_debugger007) is in settings.telegram_admin_usernames.
    """
    if user_id and settings.telegram_admin_ids and user_id in settings.telegram_admin_ids:
        return True
    if username and isinstance(username, str) and settings.telegram_admin_usernames:
        clean_user = username.strip().lstrip("@").lower()
        if clean_user in settings.telegram_admin_usernames:
            return True
    return False


def get_default_client() -> httpx.AsyncClient:
    """
    Returns an HTTPX AsyncClient.
    If running within FastAPI (e.g. on Vercel via serverless webhook),
    uses in-memory ASGITransport to eliminate network latency.
    Otherwise connects via HTTP to settings.api_base_url.
    """
    try:
        from app.main import app
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://app",
            timeout=15.0,
        )
    except Exception:
        return httpx.AsyncClient(base_url=settings.api_base_url, timeout=15.0)


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    """Display welcome message and usage instructions."""
    welcome_text = (
        "👋 <b>Welcome to Learning Center Payment Tracker Bot!</b>\n\n"
        "Available commands:\n"
        "• <b>/start</b> — Show this help message and instructions\n"
        "• <b>/debt</b> — Show debtors for the current calendar month\n"
        "• <b>/pay &lt;student_id&gt; &lt;amount&gt;</b> — Record a tuition payment for a student (Authorized users only)\n\n"
        "<b>Examples:</b>\n"
        "<code>/pay 1 200000</code>\n"
        "<code>/pay 2 150000.50</code>"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)


@dp.message(Command("debt", "debd"))
async def handle_debt(message: types.Message, client: Optional[httpx.AsyncClient] = None):
    """
    Show debtors for the current month by querying the FastAPI service over HTTP.
    """
    current_month = datetime.date.today().strftime("%Y-%m")
    path = f"/debtors?month={current_month}"

    async def _fetch(http_cli: httpx.AsyncClient):
        target = path if str(http_cli.base_url) != "http://" else f"{settings.api_base_url}{path}"
        return await http_cli.get(target)

    try:
        if client:
            resp = await _fetch(client)
        else:
            async with get_default_client() as http_cli:
                resp = await _fetch(http_cli)

        if resp.status_code != 200:
            logger.error(f"API returned status {resp.status_code} for /debtors: {resp.text}")
            await message.answer("❌ Could not retrieve debtor information from the service. Please try again later.")
            return

        data = resp.json()
        debtors = data.get("debtors", [])

        if not debtors:
            await message.answer(
                f"🎉 <b>No outstanding debtors for {current_month}!</b>\nAll students are fully paid.",
                parse_mode=ParseMode.HTML,
            )
            return

        lines = [f"📋 <b>Debtors for {current_month} ({len(debtors)} total):</b>\n"]
        for d in debtors:
            fee = Decimal(str(d.get("monthly_fee", 0)))
            paid = Decimal(str(d.get("total_paid", 0)))
            debt = Decimal(str(d.get("debt", 0)))
            lines.append(
                f"👤 <b>{d.get('name')}</b> (ID: {d.get('student_id')})\n"
                f"   Group: {d.get('group_name')}\n"
                f"   Phone: {d.get('phone')}\n"
                f"   Monthly Fee: {fee:,.2f}\n"
                f"   Total Paid: {paid:,.2f}\n"
                f"   ⚠️ <b>Remaining Debt: {debt:,.2f}</b>\n"
            )

        await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"Network error in /debt command: {e}")
        await message.answer("❌ Failed to communicate with the payment server. Please ensure the API is running.")
    except Exception as e:
        logger.error(f"Unexpected error in /debt command: {e}", exc_info=True)
        await message.answer("❌ An unexpected error occurred. Please try again later.")


@dp.message(Command("pay"))
async def handle_pay(message: types.Message, client: Optional[httpx.AsyncClient] = None):
    """
    Record a tuition payment for a student via the FastAPI REST API.
    Usage: /pay <student_id> <amount>
    Restricted to authorized administrator user IDs.
    """
    user_id = message.from_user.id if message.from_user else None
    username = message.from_user.username if message.from_user else None

    # Security check: Restrict financial operations
    if not is_user_authorized(user_id, username):
        await message.answer(
            f"⛔ <b>Access Denied:</b> You are not authorized to perform financial operations.\n"
            f"Your Telegram User ID is: <code>{user_id}</code>\n"
            f"Your Username is: <code>@{username or 'N/A'}</code>\n"
            "Please ask an administrator to whitelist your User ID or Username in <code>.env</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    text = message.text.strip() if message.text else ""
    parts = text.split()

    if len(parts) != 3:
        await message.answer(
            "❌ <b>Invalid arguments.</b>\n"
            "<b>Usage:</b> <code>/pay &lt;student_id&gt; &lt;amount&gt;</code>\n"
            "<b>Example:</b> <code>/pay 1 200000</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Validate student_id
    try:
        student_id = int(parts[1])
        if student_id <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ <b>Invalid student ID:</b> Must be a positive integer.")
        return

    # Validate amount using Decimal
    try:
        amount = Decimal(parts[2])
        if amount <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        await message.answer("❌ <b>Invalid amount:</b> Must be a positive number greater than 0.")
        return

    today_str = datetime.date.today().isoformat()
    payload = {
        "student_id": student_id,
        "amount": float(amount),
        "payment_date": today_str,
    }

    path = "/payments"

    async def _post(http_cli: httpx.AsyncClient):
        target = path if str(http_cli.base_url) != "http://" else f"{settings.api_base_url}{path}"
        return await http_cli.post(target, json=payload)

    try:
        if client:
            resp = await _post(client)
        else:
            async with get_default_client() as http_cli:
                resp = await _post(http_cli)

        if resp.status_code == 201:
            payment_data = resp.json()
            paid_amount = Decimal(str(payment_data.get("amount", amount)))
            await message.answer(
                f"✅ <b>Payment successfully recorded!</b>\n\n"
                f"💳 <b>Payment ID:</b> #{payment_data.get('id')}\n"
                f"👤 <b>Student ID:</b> {payment_data.get('student_id')}\n"
                f"💰 <b>Amount:</b> {paid_amount:,.2f}\n"
                f"📅 <b>Date:</b> {payment_data.get('payment_date')}",
                parse_mode=ParseMode.HTML,
            )
        elif resp.status_code == 404:
            await message.answer(
                f"❌ <b>Student not found:</b> No student exists with ID {student_id}.",
                parse_mode=ParseMode.HTML,
            )
        elif resp.status_code == 422:
            await message.answer(
                "❌ <b>Validation Error:</b> The payment parameters were rejected by the API.",
                parse_mode=ParseMode.HTML,
            )
        else:
            logger.error(f"API error recorded in /pay: status {resp.status_code}, response: {resp.text}")
            await message.answer(
                "❌ Failed to record payment due to a server error. Please try again later."
            )

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"Network error in /pay command: {e}")
        await message.answer("❌ Failed to communicate with the payment server. Please ensure the API is running.")
    except Exception as e:
        logger.error(f"Unexpected error in /pay command: {e}", exc_info=True)
        await message.answer(
            "❌ An unexpected error occurred while processing the payment. Please try again later."
        )


@dp.message()
async def handle_fallback(message: types.Message):
    """Handle any unrecognized messages or commands."""
    await message.answer(
        "❓ <b>Noma'lum buyruq / Unknown command.</b>\n\n"
        "Mavjud buyruqlar / Available commands:\n"
        "• <b>/start</b> — Qo'llanma / Help\n"
        "• <b>/debt</b> — Joriy oy qarzdorlari / View debtors\n"
        "• <b>/pay &lt;student_id&gt; &lt;amount&gt;</b> — To'lov kiritish / Record payment",
        parse_mode=ParseMode.HTML,
    )


async def start_bot():
    token = settings.telegram_bot_token

    if not token or token.startswith("your-") or "ABCdefGHI" in token or len(token.strip()) < 10:
        logger.error(
            "CRITICAL: TELEGRAM_BOT_TOKEN is not configured or contains a placeholder value. "
            "Please configure TELEGRAM_BOT_TOKEN in your .env file or environment variables. "
            "Exiting bot safely."
        )
        sys.exit(1)

    logger.info(f"Telegram Bot configured with API_BASE_URL: {settings.api_base_url}")
    logger.info(f"Authorized admin IDs: {settings.telegram_admin_ids}")

    bot = Bot(token=token)
    logger.info("Starting Telegram bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main():
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Telegram bot stopped.")
