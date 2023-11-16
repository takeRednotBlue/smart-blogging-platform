from fastapi import FastAPI
import uvicorn
from src.database.db import create_db_and_tables
import asyncio
from src.api.router import router

app = FastAPI()

app.include_router(router, prefix="/api")


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
