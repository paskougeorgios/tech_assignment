import enum

from sqlalchemy import Column, Integer, String, Enum
from app.database import Base


class BookStatus(str, enum.Enum):
    available = "available"
    checked_out = "checked_out"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=False)
    publication_year = Column(Integer, nullable=False)
    status = Column(Enum(BookStatus), default=BookStatus.available, nullable=False)
