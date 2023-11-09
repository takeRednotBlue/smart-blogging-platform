import uvicorn
from fastapi import FastAPI

from src.api import comments
from src.database.db import create_db_and_tables

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}

app.include_router(comments.router, prefix="/api")

if __name__ == "__main__":
    # create_db_and_tables()
    uvicorn.run(app="main:app", reload=True)