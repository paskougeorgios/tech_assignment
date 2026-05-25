# Library API

A REST API for managing library books, built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

---

## Requirements

- Docker & Docker Compose  
  _or_  
- Python 3.10+, PostgreSQL

---

## Quick Start (Docker)

```bash
# 1. Copy environment file and set your values
cp .env.example .env

# 2. Start API + PostgreSQL
docker compose up --build
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Running Locally (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # edit DATABASE_URL and API_KEY

uvicorn app.main:app --reload
```

---

## Environment Variables

| Variable       | Description                          | Example                                        |
|----------------|--------------------------------------|------------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string         | `postgresql://user:pass@localhost:5432/library`|
| `API_KEY`      | Secret key sent in `X-API-Key` header| `supersecretkey`                               |
| `APP_ENV`      | Application environment              | `development`                                  |

---

## Authentication

All endpoints require the `X-API-Key` header:

```
X-API-Key: your-secret-api-key-here
```

---

## API Endpoints

| Method | Path              | Description                                  |
|--------|-------------------|----------------------------------------------|
| GET    | `/books`          | List books (pagination + optional search)    |
| GET    | `/books/{id}`     | Get a single book                            |
| POST   | `/books`          | Create a book                                |
| PUT    | `/books/{id}`     | Update a book                                |
| DELETE | `/books/{id}`     | Delete a book                                |
| GET    | `/health`         | Health check                                 |

### Query Parameters for `GET /books`

| Param    | Type    | Default | Description                        |
|----------|---------|---------|------------------------------------|
| `page`   | integer | `1`     | Page number                        |
| `size`   | integer | `10`    | Items per page (max 100)           |
| `title`  | string  | —       | Partial, case-insensitive title search  |
| `author` | string  | —       | Partial, case-insensitive author search |

### Book Schema

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0132350884",
  "publication_year": 2008,
  "status": "available"
}
```

`status` values: `available` | `checked_out`

---

## Running Tests

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Set a test API key (the tests use settings.API_KEY)
export API_KEY=test-key
export DATABASE_URL=sqlite:///./test.db   # not used by tests; pydantic-settings requires it

pytest
```

---

## Project Structure

```
my-library-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application factory
│   ├── config.py        # pydantic-settings configuration
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models.py        # ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   └── routers/
│       ├── __init__.py
│       └── books.py     # All /books endpoints
├── tests/
│   ├── __init__.py
│   └── test_books.py    # pytest test suite
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── queries.sql          # Part 2 SQL queries
├── requirements.txt
├── .env.example
└── README.md
```

---

## SQL Queries (Part 2)

See [`queries.sql`](queries.sql) for:

1. Top 5 users by revenue in the last 3 months  
2. Products that have never been purchased  
3. Monthly revenue per category (last 6 months) with a window function  
4. Users who ordered in January but not in February  
