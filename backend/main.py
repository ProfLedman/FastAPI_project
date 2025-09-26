from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Product as ProductSchema  
from database import session, engine, get_db
import database_models
from database_models import Product 

app = FastAPI()

app.add_middleware(
    CORSMiddleware
    , allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

database_models.Base.metadata.create_all(bind=engine)  

def init_db():
    db = session()
    try:
        for product in products:
            existing_product = db.query(Product).filter(
                Product.id == product.id
            ).first()
            
            if not existing_product:
                # Convert Pydantic model to SQLAlchemy model
                db_product = Product(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    quantity=product.quantity
                )
                db.add(db_product)
                print(f"Adding product: {product.name}")
        
        db.commit()
        print("Database initialization completed successfully")
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@app.get("/products")
async def get_all_products(db: Session = Depends(get_db)):
    products = db.query(database_models.Product).all()  # Using SQLAlchemy model
    return products

@app.get("/products/{id}")
async def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == id).first()  # Using SQLAlchemy model
    if product:
        return product
    return {"error": "Product not found"}

@app.post("/products")
async def add_product(product: ProductSchema, db: Session = Depends(get_db)):  # Using Pydantic model for validation
    db_product = Product(**product.dict())  # Convert to SQLAlchemy model
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{id}")
async def update_product(id: int, updated_product: ProductSchema, db: Session = Depends(get_db)):  # Using Pydantic model
    product = db.query(Product).filter(Product.id == id).first()  # Using SQLAlchemy model
    if product:
        for key, value in updated_product.dict().items():
            setattr(product, key, value)
        db.commit()
        return {"message": "Product updated successfully"}
    return {"error": "Product not found"}

@app.delete("/products/{id}")
async def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()  # Using SQLAlchemy model
    if product:
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    return {"error": "Product not found"}