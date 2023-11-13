from logging.config import dictConfig

from fastapi import FastAPI
from src.api.router import router

# autocomplete request limiter
from src.api.autocomplete import autocomplete_rate_limiter_middleware


from src.api.router import router
from src.log_config import LogConfig

dictConfig(LogConfig().model_dump())

app = FastAPI()
app.include_router(router, prefix="/api")

# Add the rate limiter middleware
app.middleware("http")(autocomplete_rate_limiter_middleware)



@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}
