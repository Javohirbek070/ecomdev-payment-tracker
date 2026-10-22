import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from aiogram import Bot, types
from app.api import students, payments, debtors, dashboard
from app.database import init_db
from app.config import settings
from bot.main import dp

logger = logging.getLogger("telegram_webhook")

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
)


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

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(students.router)
app.include_router(payments.router)
app.include_router(debtors.router)
app.include_router(dashboard.router)

# Mount frontend static files if built
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/dashboard", include_in_schema=False)
    @app.get("/admin", include_in_schema=False)
    def serve_dashboard():
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Learning Center Payment Tracker API",
        "documentation": "/docs",
        "dashboard": "/dashboard",
    }


@app.get("/", tags=["Health"])
def root_endpoint(request: Request):
    """Root endpoint: serves Admin Dashboard to browsers, or health JSON to API clients."""
    accept = request.headers.get("accept", "")
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if "text/html" in accept and os.path.exists(index_file):
        return FileResponse(index_file)
    return health_check()


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
