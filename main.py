from logging.config import dictConfig

from fastapi import FastAPI
import uvicorn
from src.database.db import create_db_and_tables
import asyncio
from src.api.router import router
from fastapi_limiter import FastAPILimiter

from src.api import comments
from src.conf.config import settings

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from src.api.router import router
from src.conf.config import settings
from src.log_config import LogConfig

dictConfig(LogConfig().model_dump())

app = FastAPI()

app.include_router(comments.router, prefix="/api")
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup():
    r = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}


# async def startup_event():
#     await create_db_and_tables()


# if __name__ == "__main__":
#     # Создаем событие запуска приложения
#     app.add_event_handler("startup", startup_event)

#     # Запускаем Uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
