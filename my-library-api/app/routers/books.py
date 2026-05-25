from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app import models, schemas
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/books", tags=["books"])

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key


# ── GET /books ─────────────────────────────────────────────────────────────────

@router.get("", response_model=schemas.PaginatedBooks)
def list_books(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    title: str | None = Query(None, description="Filter by title (partial match)"),
    author: str | None = Query(None, description="Filter by author (partial match)"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    query = db.query(models.Book)

    if title or author:
        filters = []
        if title:
            filters.append(models.Book.title.ilike(f"%{title}%"))
        if author:
            filters.append(models.Book.author.ilike(f"%{author}%"))
        query = query.filter(or_(*filters))

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return schemas.PaginatedBooks(total=total, page=page, size=size, items=items)


# ── GET /books/{id} ────────────────────────────────────────────────────────────

@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


# ── POST /books ────────────────────────────────────────────────────────────────

@router.post("", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    payload: schemas.BookCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    existing = db.query(models.Book).filter(models.Book.isbn == payload.isbn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with ISBN '{payload.isbn}' already exists",
        )
    book = models.Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


# ── PUT /books/{id} ────────────────────────────────────────────────────────────

@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    payload: schemas.BookUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    updates = payload.model_dump(exclude_unset=True)
    if "isbn" in updates and updates["isbn"] != book.isbn:
        conflict = db.query(models.Book).filter(models.Book.isbn == updates["isbn"]).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with ISBN '{updates['isbn']}' already exists",
            )

    for field, value in updates.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


# ── DELETE /books/{id} ─────────────────────────────────────────────────────────

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    db.delete(book)
    db.commit()
