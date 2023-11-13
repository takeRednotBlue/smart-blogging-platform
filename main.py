from logging.config import dictConfig

from fastapi import FastAPI

from src.api.router import router
from src.log_config import LogConfig

dictConfig(LogConfig().model_dump())

app = FastAPI()
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}
