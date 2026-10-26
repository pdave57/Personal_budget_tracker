from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    category = relationship("Category")

    __table_args__ = (
        UniqueConstraint("category_id", "month", "year", name="uq_category_month_year"),
    )