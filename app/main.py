import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, types
from app.api import students, payments, debtors
from app.database import init_db
from app.config import settings
from bot.main import dp

logger = logging.getLogger("telegram_webhook")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(
    title="Learning Center Payment Tracker",
    description="Mini-system for tracking students, monthly tuition payments, and debtors.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register API routers
app.include_router(students.router)
app.include_router(payments.router)
app.include_router(debtors.router)


@app.get("/health", tags=["Health"])
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Learning Center Payment Tracker API",
        "documentation": "/docs",
    }


@app.post("/webhook/telegram", tags=["Telegram Bot"])
async def telegram_webhook(request: Request):
    """Serverless webhook endpoint to receive and process Telegram updates on Vercel."""
    token = settings.telegram_bot_token
    if not token or len(token.strip()) < 10:
        return {"ok": False, "error": "Bot token not configured"}

    bot = Bot(token=token)
    try:
        data = await request.json()
        update = types.Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
    finally:
        await bot.session.close()

    return {"ok": True}
