from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

# --- Database Configuration ---
# Connection String: mysql+pymysql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost:3307/todo_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQL Table Model ---
class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100)) # SQL VARCHAR(100)
    is_completed = Column(Boolean, default=False)

# Create Tables (Automatically runs "CREATE TABLE IF NOT EXISTS")
Base.metadata.create_all(bind=engine)

# --- Pydantic Schema (For API Validation) ---
class TodoCreate(BaseModel):
    title: str
    is_completed: bool = False

class TodoResponse(TodoCreate):
    id: int
    class Config:
        orm_mode = True

# --- App Setup ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    # Translates to: INSERT INTO todos (title, is_completed) VALUES (...)
    db_todo = TodoDB(title=todo.title, is_completed=todo.is_completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model=List[TodoResponse])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Translates to: SELECT * FROM todos LIMIT 100
    todos = db.query(TodoDB).offset(skip).limit(limit).all()
    return todos

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    # Translates to: DELETE FROM todos WHERE id = ...
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Deleted"}