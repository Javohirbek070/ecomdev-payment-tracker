import asyncio
import datetime
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

from app.config import settings
from app.database import SessionLocal, init_db
from app.schemas import PaymentCreate
from app import crud
from app.services.debtors import get_monthly_debtors
from app.exceptions import StudentNotFoundError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram_bot")

dp = Dispatcher()


def is_user_authorized(user_id: int) -> bool:
    """
    Check if the user is authorized to perform financial actions.
    If TELEGRAM_ADMIN_IDS is configured, only users in that list are allowed.
    """
    if not settings.telegram_admin_ids:
        # If no admin IDs are configured, restrict financial operations by default for security
        return False
    return user_id in settings.telegram_admin_ids


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    """Display welcome message and usage instructions."""
    welcome_text = (
        "👋 <b>Welcome to Learning Center Payment Tracker Bot!</b>\n\n"
        "Available commands:\n"
        "• <b>/start</b> — Show this help message and instructions\n"
        "• <b>/debt</b> — Show debtors for the current month\n"
        "• <b>/pay &lt;student_id&gt; &lt;amount&gt;</b> — Record a payment for a student (Authorized users only)\n\n"
        "<b>Examples:</b>\n"
        "<code>/pay 1 200000</code>\n"
        "<code>/pay 2 150000.50</code>"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)


@dp.message(Command("debt"))
async def handle_debt(message: types.Message):
    """Show debtors for the current month."""
    current_month = datetime.date.today().strftime("%Y-%m")

    try:
        with SessionLocal() as db:
            result = get_monthly_debtors(db, current_month)

        if not result.debtors:
            await message.answer(
                f"🎉 <b>No outstanding debtors for {current_month}!</b>\nAll students are fully paid.",
                parse_mode=ParseMode.HTML,
            )
            return

        lines = [f"📋 <b>Debtors for {current_month} ({len(result.debtors)} total):</b>\n"]
        for d in result.debtors:
            lines.append(
                f"👤 <b>{d.name}</b> (ID: {d.student_id})\n"
                f"   Group: {d.group_name}\n"
                f"   Phone: {d.phone}\n"
                f"   Monthly Fee: {d.monthly_fee:,.2f}\n"
                f"   Total Paid: {d.total_paid:,.2f}\n"
                f"   ⚠️ <b>Remaining Debt: {d.debt:,.2f}</b>\n"
            )

        await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error fetching debtors in /debt command: {e}", exc_info=True)
        await message.answer(
            "❌ An error occurred while retrieving debtors. Please try again later."
        )


@dp.message(Command("pay"))
async def handle_pay(message: types.Message):
    """
    Record a tuition payment for a student.
    Usage: /pay <student_id> <amount>
    Restricted to authorized administrator user IDs.
    """
    user_id = message.from_user.id if message.from_user else None

    # Security check: Restrict financial operations
    if user_id is None or not is_user_authorized(user_id):
        await message.answer(
            "⛔ <b>Access Denied:</b> You are not authorized to perform financial operations.\n"
            "Please contact the system administrator to whitelist your Telegram User ID.",
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

    # Validate amount
    try:
        amount = float(parts[2])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ <b>Invalid amount:</b> Must be a positive number greater than 0.")
        return

    # Process payment
    try:
        today = datetime.date.today()
        with SessionLocal() as db:
            student = crud.get_student(db, student_id)
            if not student:
                await message.answer(
                    f"❌ <b>Student not found:</b> No student exists with ID {student_id}.",
                    parse_mode=ParseMode.HTML,
                )
                return

            payment = crud.create_payment(
                db,
                PaymentCreate(
                    student_id=student_id,
                    amount=amount,
                    payment_date=today,
                ),
            )

            await message.answer(
                f"✅ <b>Payment successfully recorded!</b>\n\n"
                f"💳 <b>Payment ID:</b> #{payment.id}\n"
                f"👤 <b>Student:</b> {student.name} (ID: {student.id})\n"
                f"📚 <b>Group:</b> {student.group_name}\n"
                f"💰 <b>Amount:</b> {payment.amount:,.2f}\n"
                f"📅 <b>Date:</b> {payment.payment_date}",
                parse_mode=ParseMode.HTML,
            )
    except StudentNotFoundError:
        await message.answer(
            f"❌ <b>Student not found:</b> No student exists with ID {student_id}.",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Error recording payment in /pay command: {e}", exc_info=True)
        await message.answer(
            "❌ An unexpected error occurred while processing the payment. Please try again later."
        )


async def main():
    token = settings.telegram_bot_token

    if not token or token.startswith("your-") or "ABCdefGHI" in token:
        logger.error(
            "CRITICAL: TELEGRAM_BOT_TOKEN is not configured or contains a placeholder value. "
            "Please configure TELEGRAM_BOT_TOKEN in your .env file or environment variables. "
            "Exiting bot safely."
        )
        sys.exit(1)

    logger.info("Initializing database tables...")
    init_db()

    bot = Bot(token=token)
    logger.info("Starting Telegram bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Telegram bot stopped.")
