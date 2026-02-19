import time
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from fastapi.middleware.cors import CORSMiddleware

# --- Database Configuration ---
# Get DB URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://user:password@127.0.0.1:3306/todo_db"
)

# --- THE FIX: Retry Logic ---
def wait_for_db_connection(retries=10, delay=3):
    """Wait for the database to be ready before starting."""
    print(f"Checking DB connection to: {SQLALCHEMY_DATABASE_URL}...")
    for i in range(retries):
        try:
            # Try to create a temporary engine just to check connection
            temp_engine = create_engine(SQLALCHEMY_DATABASE_URL)
            with temp_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return temp_engine
        except OperationalError as e:
            print(f"⚠️ Database not ready yet (Attempt {i+1}/{retries}). Retrying in {delay}s...")
            time.sleep(delay)
    raise Exception("❌ Could not connect to the database after multiple retries.")

# Initialize Engine with the retry logic
engine = wait_for_db_connection()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQL Table Model ---
class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    is_completed = Column(Boolean, default=False)

# Create Tables
Base.metadata.create_all(bind=engine)

# --- Pydantic Schema ---
class TodoCreate(BaseModel):
    title: str
    is_completed: bool = False

class TodoResponse(TodoCreate):
    id: int
    class Config:
        from_attributes = True

# --- App Setup ---
app = FastAPI()

# --- CORS Configuration (UPDATED) ---
# We explicitly list the origins to allow the browser to trust us
origins = [
    "http://localhost:5173",    # React App (Localhost)
    "http://127.0.0.1:5173",    # React App (IP)
    "http://localhost:8000",    # Backend (Self)
    "http://3.82.142.12:8000",    # Backend (IP)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # <--- The Critical Fix
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

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "healthy", "database": "connected"}

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoDB(title=todo.title, is_completed=todo.is_completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model=List[TodoResponse])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = db.query(TodoDB).offset(skip).limit(limit).all()
    return todos

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Deleted"}