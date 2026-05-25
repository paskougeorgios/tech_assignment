from pydantic import BaseModel, Field
from typing import Optional
from app.models import BookStatus


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=1, max_length=20)
    publication_year: int = Field(..., ge=1000, le=9999)
    status: BookStatus = BookStatus.available


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=1, max_length=20)
    publication_year: Optional[int] = Field(None, ge=1000, le=9999)
    status: Optional[BookStatus] = None


class BookResponse(BookBase):
    id: int

    model_config = {"from_attributes": True}


class PaginatedBooks(BaseModel):
    total: int
    page: int
    size: int
    items: list[BookResponse]
