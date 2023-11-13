from fastapi import FastAPI
from src.api.router import router

# autocomplete request limiter
from src.api.autocomplete import autocomplete_rate_limiter_middleware


app = FastAPI()
app.include_router(router, prefix="/api")

# Add the rate limiter middleware
app.middleware("http")(autocomplete_rate_limiter_middleware)


@app.get("/")
def root():
    return {"message": "Smart Blogging Platform API"}
