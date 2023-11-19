from logging.config import dictConfig

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.api.router import router
from src.conf.config import settings
from src.log_config import LogConfig

dictConfig(LogConfig().model_dump())

app = FastAPI()

app.include_router(router, prefix="/api")


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
