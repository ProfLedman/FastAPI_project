from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text

# Import from updated modules
from database import engine, get_db, Base
from database_models import Product
from models import ProductCreate, ProductUpdate, Product as ProductResponse

app = FastAPI(
    title="Product API",
    description="A professional FastAPI product management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # In production, use specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create tables
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    # You could add initial data seeding here

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    return {"message": "Product API is running", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check including database connectivity"""
    try:
        # Get PostgreSQL version using text() for raw SQL
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "version": version,
                "type": "PostgreSQL"
            },
            "api_version": app.version
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": {
                    "connected": False,
                    "error": str(e)
                }
            }
        )

# Product endpoints
@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
async def get_all_products(
    skip: int = 0, 
    limit: int = 100,  # Added pagination
    db: Session = Depends(get_db)
):
    """Get all products with pagination"""
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    try:
        # Check if product name already exists
        existing_product = db.query(Product).filter(Product.name == product.name).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this name already exists"
            )
        
        # Create new product using dict unpacking
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
        
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )
    
@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update an existing product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Update only provided fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", tags=["Products"])
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)