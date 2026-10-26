from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    description = Column(String, nullable=True)
    transaction_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    category = relationship("Category")
