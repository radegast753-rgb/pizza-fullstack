from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///./pizza.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PizzaItem(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)

Base.metadata.create_all(bind=engine)

class PizzaCreate(BaseModel):
    name: str
    price: float
    description: str
    image_url: str

class PizzaResponse(PizzaCreate):
    id: int

    class Config:
        from_attributes = True

app = FastAPI(title="Pizza Restaurant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/menu", response_model=List[PizzaResponse])
async def get_menu(db: Session = Depends(get_db)):
    items = db.query(PizzaItem).all()
    return items

@app.post("/api/menu", response_model=PizzaResponse)
async def create_pizza(pizza: PizzaCreate, db: Session = Depends(get_db)):
    new_pizza = PizzaItem(
        name=pizza.name,
        price=pizza.price,
        description=pizza.description,
        image_url=pizza.image_url
    )
    db.add(new_pizza)
    db.commit()
    db.refresh(new_pizza)
    return new_pizza

@app.delete("/api/menu")
def clear_all_menu(db: Session = Depends(get_db)):
    db.query(PizzaItem).delete()
    db.commit()
    return {"message": "All items deleted successfully"}

@app.delete("/api/menu/{pizza_id}")
def delete_pizza(pizza_id: int, db: Session = Depends(get_db)):
    pizza = db.query(PizzaItem).filter(PizzaItem.id == pizza_id).first()
    if not pizza:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(pizza)
    db.commit()
    return {"message": "Item deleted successfully"}

@app.post("/api/menu/reset")
def reset_to_demo_db(db: Session = Depends(get_db)):
    db.query(PizzaItem).delete()
    demo_items = [
        PizzaItem(name="Espresso", price=3.00, description="Rich and intense classic black coffee", image_url="https://tse1.mm.bing.net/th/id/OIP.0QpNtb2cE5OZTjFN2NQULQHaFC?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"),
        PizzaItem(name="Pizza Margherita", price=12.00, description="Classic fresh tomato sauce and melted mozzarella", image_url="https://tse1.mm.bing.net/th/id/OIP.0QpNtb2cE5OZTjFN2NQULQHaFC?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"),
        PizzaItem(name="Caesar Salad", price=9.50, description="Crispy romaine, parmesan, croutons, and creamy dressing", image_url="https://tse1.mm.bing.net/th/id/OIP.0QpNtb2cE5OZTjFN2NQULQHaFC?r=0&rs=1&pid=ImgDetMain&o=7&rm=3")
    ]
    db.add_all(demo_items)
    db.commit()
    return {"message": "Demo items loaded successfully"}