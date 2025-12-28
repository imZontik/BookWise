from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.adapters.endpoints.auth import router as auth_router
from src.adapters.endpoints.author import router as author_router
from src.adapters.endpoints.books.books import router as books_router
from src.adapters.endpoints.books.favourites import router as favourite_books_router
from src.adapters.endpoints.reviews import router as reviews_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app():
    _app = FastAPI(
        title="Hotel API",
        description="API for hotels",
        version="1.0",
        lifespan=lifespan
    )

    _app.include_router(auth_router)
    _app.include_router(author_router)

    _app.include_router(books_router)
    _app.include_router(favourite_books_router)

    _app.include_router(reviews_router)

    return _app


app = create_app()

Instrumentator(
    excluded_handlers=["/metrics", "/docs", "/openapi.json"]
).instrument(app).expose(app, endpoint="/metrics")