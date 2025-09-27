from pydantic import BaseModel, Field, validator
from typing import Optional

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Laptop")
    description: Optional[str] = Field(None, max_length=500, example="High-performance gaming laptop")
    price: float = Field(..., gt=0, example=999.99)  # Price must be greater than 0
    quantity: int = Field(..., ge=0, example=10)  # Quantity must be >= 0

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class ProductCreate(ProductBase):
    """Schema for creating a product (no ID needed)"""
    pass

class ProductUpdate(ProductBase):
    """Schema for updating a product (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)

class Product(ProductBase):
    """Schema for returning a product (includes ID)"""
    id: int

    class Config:
        orm_mode = True  # Allows conversion from ORM object
