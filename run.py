import asyncio
import logging
import uvicorn

from app.config import settings
from app.database import init_db
from app.main import app
from bot.main import start_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("learning_center_runner")


async def run_server():
    """Start Uvicorn ASGI server."""
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    logger.info("Initializing database schema...")
    init_db()

    logger.info("Starting FastAPI server and Telegram Bot concurrently...")
    await asyncio.gather(
        run_server(),
        start_bot(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application stopped.")
