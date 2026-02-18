from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

# 1. Move Middleware UP (Before routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Todo(BaseModel):
    id: Optional[str] = None
    title: str
    is_completed: bool = False

db: List[Todo] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Enterprise ToDo API v1"}

@app.get("/todos", response_model=List[Todo])
def get_todos():
    return db

@app.post("/todos", response_model=Todo)
def create_todo(todo: Todo):
    todo.id = str(uuid.uuid4())
    db.append(todo)
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str):
    global db
    initial_length = len(db)
    db = [t for t in db if t.id != todo_id]
    
    if len(db) == initial_length:
        raise HTTPException(status_code=404, detail="Todo not found")
        
    return {"message": "Deleted successfully"}
