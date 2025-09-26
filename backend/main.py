from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import Product as ProductSchema  # Rename to avoid confusion
from database import session, engine, get_db
import database_models
from database_models import Product  # Import the SQLAlchemy model

app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)  

products = [Product(id=1, name="Laptop", description="A high-end laptop", price=1500.00, quantity=10),
            Product(id=2, name="Smartphone", description="A latest model smartphone", price=800.00, quantity=25),
            Product(id=3, name="Headphones", description="Noise-cancelling headphones", price=200.00, quantity=50),
            Product(id=4, name="Monitor", description="4K UHD Monitor", price=400.00, quantity=15),
            Product(id=5, name="Keyboard", description="Mechanical keyboard", price=100.00, quantity=30),
            Product(id=6, name="Mouse", description="Wireless mouse", price=50.00, quantity=40),
            Product(id=7, name="Printer", description="All-in-one printer", price=250.00, quantity=8),
            Product(id=8, name="Tablet", description="10-inch tablet", price=300.00, quantity=20),
            Product(id=9, name="Camera", description="Digital SLR camera", price=1200.00, quantity=5),
            Product(id=10, name="Smartwatch", description="Fitness smartwatch", price=150.00, quantity=35),
            Product(id=11, name="External Hard Drive", description="2TB external hard drive", price=100.00, quantity=12),
            Product(id=12, name="Router", description="Wi-Fi 6 router", price=180.00, quantity=18),
            Product(id=13, name="Speakers", description="Bluetooth speakers", price=80.00, quantity=22),
            Product(id=14, name="Webcam", description="HD webcam", price=70.00, quantity=28),
            Product(id=15, name="Microphone", description="USB microphone", price=120.00, quantity=14),
            Product(id=16, name="Charger", description="Fast charger", price=40.00, quantity=45),
            Product(id=17, name="Projector", description="1080p projector", price=600.00, quantity=7),
            Product(id=18, name="Gaming Console", description="Latest gaming console", price=500.00, quantity=9),
            Product(id=19, name="VR Headset", description="Virtual reality headset", price=350.00, quantity=11),
            Product(id=20, name="Smart Home Hub", description="Voice-controlled smart home hub", price=130.00, quantity=16),
            Product(id=21, name="Fitness Tracker", description="Activity and sleep tracker", price=90.00, quantity=27),
            Product(id=22, name="E-reader", description="6-inch e-reader", price=110.00, quantity=13),
            Product(id=23, name="Drone", description="Quadcopter drone", price=400.00, quantity=6),
            Product(id=24, name="Action Camera", description="4K action camera", price=250.00, quantity=19),
            Product(id=25, name="Smart Light Bulb", description="Color-changing smart bulb", price=30.00, quantity=33),
            Product(id=26, name="Electric Scooter", description="Foldable electric scooter", price=700.00, quantity=4)]



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
    products = db.query(Product).all()  # Using SQLAlchemy model
    return products

@app.get("/products/{id}")
async def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()  # Using SQLAlchemy model
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