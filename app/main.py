from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import students, payments, debtors
from app.database import init_db


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
