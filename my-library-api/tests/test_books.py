import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Use an in-memory SQLite database for tests
SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables once for the test session
Base.metadata.create_all(bind=engine)

client = TestClient(app)

VALID_HEADERS = {"X-API-Key": settings.API_KEY}

SAMPLE_BOOK = {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "publication_year": 2008,
    "status": "available",
}


@pytest.fixture(autouse=True)
def clean_db():
    """Truncate books table before each test for isolation."""
    yield
    from app.models import Book
    db = TestingSessionLocal()
    db.query(Book).delete()
    db.commit()
    db.close()


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_create_and_get_book():
    """Happy path: create a book and retrieve it by ID."""
    response = client.post("/books", json=SAMPLE_BOOK, headers=VALID_HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == SAMPLE_BOOK["title"]
    assert data["isbn"] == SAMPLE_BOOK["isbn"]
    book_id = data["id"]

    get_response = client.get(f"/books/{book_id}", headers=VALID_HEADERS)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == book_id


def test_list_books_with_pagination():
    """Happy path: list books respects pagination parameters."""
    for i in range(5):
        client.post(
            "/books",
            json={**SAMPLE_BOOK, "isbn": f"978-000000000{i}"},
            headers=VALID_HEADERS,
        )

    response = client.get("/books?page=1&size=3", headers=VALID_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert len(body["items"]) == 3
    assert body["page"] == 1
    assert body["size"] == 3


def test_update_book():
    """Happy path: update an existing book's status."""
    create_resp = client.post("/books", json=SAMPLE_BOOK, headers=VALID_HEADERS)
    book_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/books/{book_id}",
        json={"status": "checked_out"},
        headers=VALID_HEADERS,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "checked_out"


def test_delete_book():
    """Happy path: delete a book and confirm 404 on subsequent GET."""
    create_resp = client.post("/books", json=SAMPLE_BOOK, headers=VALID_HEADERS)
    book_id = create_resp.json()["id"]

    del_resp = client.delete(f"/books/{book_id}", headers=VALID_HEADERS)
    assert del_resp.status_code == 204

    get_resp = client.get(f"/books/{book_id}", headers=VALID_HEADERS)
    assert get_resp.status_code == 404


def test_search_by_title():
    """Happy path: search books by title returns matching results."""
    client.post("/books", json=SAMPLE_BOOK, headers=VALID_HEADERS)
    client.post(
        "/books",
        json={**SAMPLE_BOOK, "title": "The Pragmatic Programmer", "isbn": "978-0201616224"},
        headers=VALID_HEADERS,
    )

    response = client.get("/books?title=clean", headers=VALID_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Clean Code"


# ── Error cases ────────────────────────────────────────────────────────────────

def test_get_nonexistent_book_returns_404():
    """Error case: fetching a book that does not exist returns 404."""
    response = client.get("/books/99999", headers=VALID_HEADERS)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_duplicate_isbn_returns_409():
    """Error case: creating a book with a duplicate ISBN returns 409."""
    client.post("/books", json=SAMPLE_BOOK, headers=VALID_HEADERS)
    response = client.post("/books", json=SAMPLE_BOOK, headers=VALID_HEADERS)
    assert response.status_code == 409


def test_create_book_invalid_payload_returns_422():
    """Error case: missing required fields returns 422 Unprocessable Entity."""
    response = client.post("/books", json={"title": "No ISBN"}, headers=VALID_HEADERS)
    assert response.status_code == 422


# ── Auth cases ─────────────────────────────────────────────────────────────────

def test_missing_api_key_returns_403():
    """Auth: request without X-API-Key header is rejected with 403."""
    response = client.get("/books")
    assert response.status_code == 403


def test_invalid_api_key_returns_403():
    """Auth: request with wrong API key is rejected with 403."""
    response = client.get("/books", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403


def test_valid_api_key_is_accepted():
    """Auth: request with correct API key succeeds."""
    response = client.get("/books", headers=VALID_HEADERS)
    assert response.status_code == 200
