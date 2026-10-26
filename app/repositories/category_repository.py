from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int, category_id: int) -> Optional[Category]:
        return (
            self.db.query(Category)
            .filter(Category.id == category_id, Category.user_id == user_id)
            .first()
        )

    def get_by_name(self, user_id: int, name: str) -> Optional[Category]:
        return (
            self.db.query(Category)
            .filter(Category.name == name, Category.user_id == user_id)
            .first()
        )

    def get_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Category]:
        return (
            self.db.query(Category)
            .filter(Category.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(self, user_id: int, type: str) -> List[Category]:
        return (
            self.db.query(Category)
            .filter(Category.type == type, Category.user_id == user_id)
            .all()
        )

    def create(self, category: Category, user_id: int) -> Category:
        category.user_id = user_id
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, user_id: int, category_id: int) -> bool:
        category = self.get_by_id(user_id, category_id)
        if category:
            self.db.delete(category)
            self.db.commit()
            return True
        return False
