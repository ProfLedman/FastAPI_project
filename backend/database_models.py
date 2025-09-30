from sqlalchemy import Column, Integer, String, Float, Sequence
from database import Base  # Import from centralized location

class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer, 
        Sequence('products_id_seq', start=1, increment=1, minvalue=1),
        primary_key=True, 
        index=True,
        nullable=False
    )
    name = Column(String(100), index=True, nullable=False)  # Added length limit and not null
    description = Column(String(500), index=True)  # Added reasonable length
    price = Column(Float, nullable=False)  # Price should not be null
    quantity = Column(Integer, default=0)  # Added default value

    def to_dict(self):
        """Helper method to convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity
        }