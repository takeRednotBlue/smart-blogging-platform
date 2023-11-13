from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from src.api import comments
from src.database.db import create_db_and_tables
from src.conf.config import settings

app = FastAPI()

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


app.include_router(comments.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", reload=True)

    # import asyncio
    # asyncio.run(create_db_and_tables())
