from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.quiz import Category
from app.schemas.quiz import CategoryCreate, CategoryResponse

router = APIRouter()

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new quiz category
    Check if category with the same name already exists
    """
    # Lowercase check to avoid duplicates like 'Python' and 'python'
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(
            status_code=400, 
            detail="Category already exists"
        )
    
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """
    Retrieve all quiz categories
    """
    return db.query(Category).all()