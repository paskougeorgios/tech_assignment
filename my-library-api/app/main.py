from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import books

# Create all tables on startup (suitable for development; use Alembic for production migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library API",
    description="REST API for managing library books",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
