# FastAPI Project Setup Guide

This is a complete FastAPI project starter template following best practices.

## Project Structure

```
FastAPI Test/
├── venv/                 # Virtual environment (created after setup)
├── main.py              # Main application file
├── requirements.txt     # Project dependencies
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Setup Instructions

### Step 1: Create Virtual Environment

```bash
# On Windows
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
# Option 1: Using Python directly (development)
python main.py

# Option 2: Using uvicorn directly (with auto-reload)
uvicorn main:app --reload

# For production
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at: **http://127.0.0.1:8000**

## Interactive API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Key FastAPI Concepts

### 1. **Pydantic Models**
Define request/response data validation using `BaseModel`:
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None
```

### 2. **HTTP Methods**
- `@app.get()` - Retrieve data
- `@app.post()` - Create data
- `@app.put()` - Update data completely
- `@app.delete()` - Delete data
- `@app.patch()` - Partial update

### 3. **Path Parameters**
```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}
```

### 4. **Query Parameters**
```python
@app.get("/search")
async def search(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

### 5. **Request Body**
```python
@app.post("/items")
async def create_item(item: Item):
    return item
```

### 6. **Response Models**
Control the response format:
```python
@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item) -> ItemResponse:
    return ItemResponse(...)
```

## Testing the API

### Using curl

```bash
# GET request
curl http://127.0.0.1:8000/

# GET with parameters
curl "http://127.0.0.1:8000/items/123"

# POST request with JSON
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Widget","price":29.99,"tax":2.99}'
```

### Using Python requests

```python
import requests

# GET
response = requests.get("http://127.0.0.1:8000/items/123")

# POST
data = {"name": "Widget", "price": 29.99, "tax": 2.99}
response = requests.post("http://127.0.0.1:8000/items", json=data)

print(response.json())
```

## Best Practices

✅ **Do:**
- Use virtual environments for project isolation
- Define Pydantic models for data validation
- Use async functions for better performance
- Add docstrings to endpoints
- Use path/query parameters correctly
- Include response models for documentation

❌ **Avoid:**
- Running without virtual environment
- Mixing dependencies across projects
- Returning plain dictionaries in production
- Ignoring type hints
- Deploying with `--reload` in production

## Next Steps

1. Test each endpoint in Swagger UI at `/docs`
2. Modify the example endpoints to match your use case
3. Add database integration (SQLAlchemy, SQLModel)
4. Add authentication/authorization (JWT, OAuth2)
5. Add request validation and error handling
6. Deploy to production (Docker, Heroku, AWS, etc.)

## Useful Resources

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
