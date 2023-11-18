from logging.config import dictConfig

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.api.router import router
from src.conf.config import settings
from src.log_config import LogConfig

dictConfig(LogConfig().model_dump())

app = FastAPI()
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}


@app.on_event("startup")
async def startup():
    r = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", reload=True)

    # import asyncio
    # from src.database.db import create_db_and_tables
    # asyncio.run(create_db_and_tables())
