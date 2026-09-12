from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.database import engine
from fastapi import FastAPI
from app.api.routes.routers.chat import router as chat_router
from app.api.routes.routers.analyze import router as analyze_router
from app.api.routes.routers.auth import router as auth_router
from app.api.routes.routers.conversations import router as conversations_router
import logging
from app.api.routes.routers.messages import router as messages_router
from app.services.redis_service import test_redis_connection
import time
from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="LLM App",
    version="1.0.0",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    logging.info(
        "%s %s | status=%s | duration=%.3fs",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response


app.include_router(chat_router)
app.include_router(analyze_router)
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(messages_router)


@app.get("/health")
def health_check():
    database_status = False

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            database_status = True
    except Exception:
        database_status = False

    redis_status = test_redis_connection()

    overall_status = database_status and redis_status

    return {
        "status": overall_status,
        "service": "LLM App",
        "database": database_status,
        "redis": redis_status,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(
        "Unhandled exception | %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Internal server error. Please try again later.",
        },
    )
