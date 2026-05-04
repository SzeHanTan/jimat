from fastapi import FastAPI
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI(
    title="My FastAPI App",
    description="A simple FastAPI application",
    version="1.0.0"
)

# Define request/response models using Pydantic
class Item(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None

class ItemResponse(BaseModel):
    message: str
    item: Item
    total_price: float

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Welcome endpoint"""
    return {"message": "Welcome to FastAPI!"}

# GET endpoint with path parameter
@app.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int):
    """Get an item by ID"""
    return {"item_id": item_id, "name": f"Item {item_id}"}

# GET endpoint with query parameters
@app.get("/search", tags=["items"])
async def search_items(skip: int = 0, limit: int = 10):
    """Search items with pagination"""
    return {"skip": skip, "limit": limit, "results": []}

# POST endpoint with request body
@app.post("/items", response_model=ItemResponse, tags=["items"])
async def create_item(item: Item):
    """Create a new item"""
    total_price = item.price + (item.tax if item.tax else 0)
    return {
        "message": "Item created successfully",
        "item": item,
        "total_price": total_price
    }

# PUT endpoint to update an item
@app.put("/items/{item_id}", tags=["items"])
async def update_item(item_id: int, item: Item):
    """Update an existing item"""
    return {"item_id": item_id, "updated_item": item}

# DELETE endpoint
@app.delete("/items/{item_id}", tags=["items"])
async def delete_item(item_id: int):
    """Delete an item"""
    return {"message": f"Item {item_id} deleted successfully"}

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Check if the API is running"""
    return {"status": "healthy"}
