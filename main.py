from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///./pizza.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB MODEL ----------------
class PizzaItem(Base):
    __tablename__ = "menu"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    image_url = Column(String)
    category = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------- SCHEMAS ----------------
class PizzaCreate(BaseModel):
    name: str
    price: float
    description: str
    image_url: str
    category: str

class PizzaResponse(PizzaCreate):
    id: int

    class Config:
        from_attributes = True

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- API ----------------
@app.get("/api/menu", response_model=List[PizzaResponse])
def get_menu(db: Session = Depends(get_db)):
    return db.query(PizzaItem).all()

@app.post("/api/menu", response_model=PizzaResponse)
def create_item(item: PizzaCreate, db: Session = Depends(get_db)):
    obj = PizzaItem(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/api/menu/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.query(PizzaItem).filter(PizzaItem.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

@app.delete("/api/menu")
def clear(db: Session = Depends(get_db)):
    db.query(PizzaItem).delete()
    db.commit()
    return {"ok": True}