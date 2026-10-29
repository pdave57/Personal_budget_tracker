from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/categories", tags=["Categories"])


def get_category_service(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    service: CategoryRepository = Depends(get_category_service),
    current_user: User = Depends(get_current_active_user),
):
    existing = service.get_by_name(current_user.id, data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    category = Category(**data.model_dump())
    category = service.create(category, current_user.id)
    return category


@router.get("", response_model=List[CategoryResponse])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    service: CategoryRepository = Depends(get_category_service),
    current_user: User = Depends(get_current_active_user),
):
    return service.get_all(current_user.id, skip, limit)


@router.get("/type/{type}", response_model=List[CategoryResponse])
def get_categories_by_type(
    type: str,
    service: CategoryRepository = Depends(get_category_service),
    current_user: User = Depends(get_current_active_user),
):
    if type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Type must be 'income' or 'expense'")
    return service.get_by_type(current_user.id, type)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    service: CategoryRepository = Depends(get_category_service),
    current_user: User = Depends(get_current_active_user),
):
    category = service.get_by_id(current_user.id, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    service: CategoryRepository = Depends(get_category_service),
    current_user: User = Depends(get_current_active_user),
):
    category = service.get_by_id(current_user.id, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    return service.update(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    service: CategoryRepository = Depends(get_category_service),
    current_user: User = Depends(get_current_active_user),
):
    if not service.delete(current_user.id, category_id):
        raise HTTPException(status_code=404, detail="Category not found")