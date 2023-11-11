from fastapi import FastAPI
from src.api import tags

app = FastAPI()
app.include_router(tags.router, prefix='/api')


@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}
