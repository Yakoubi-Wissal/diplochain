from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def get_all(db: AsyncSession = Depends(get_db)):
    """Get all items"""
    return {"message": "List of worker", "items": []}

@router.get("/{id}")
async def get_one(id: int, db: AsyncSession = Depends(get_db)):
    """Get a single item by ID"""
    return {"message": f"worker {id}", "id": id}

@router.post("/")
async def create(db: AsyncSession = Depends(get_db)):
    """Create a new item"""
    return {"message": "Create worker", "id": 1}

@router.put("/{id}")
async def update(id: int, db: AsyncSession = Depends(get_db)):
    """Update an item"""
    return {"message": f"Update worker {id}", "id": id}

@router.delete("/{id}")
async def delete(id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item"""
    return {"message": f"Delete worker {id}", "id": id}
