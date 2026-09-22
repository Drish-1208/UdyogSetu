from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our database tools and recipe book
from database import SessionLocal
import models

app = FastAPI()

# 1. The Order Ticket (Pydantic Schema)
# This makes sure the user gives us exactly these three things
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

# 2. Opening the Fridge Door (Database Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Just our friendly hello message from before
@app.get("/")
def read_root():
    return {"Message": "Hello! The government portal backend is awake!"}

# 3. The New Endpoint to Add a User
@app.post("/users/")
def create_test_user(user_data: UserCreate, db: Session = Depends(get_db)):
    
    # Remember our models.py? It says every user MUST have a role.
    # So first, let's create a dummy "entrepreneur" role if it doesn't exist yet.
    role = db.query(models.Role).filter(models.Role.role_name == "entrepreneur").first()
    if not role:
        role = models.Role(role_name="entrepreneur")
        db.add(role)
        db.commit()
        db.refresh(role)

    # Now, let's create the actual user using the data from the order ticket!
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=user_data.password, # In a real app, we would scramble (hash) this!
        role_id=role.id
    )
    
    # Put the new user in the database and save (commit) it
    db.add(new_user)
    db.commit()
    
    return {"message": "Success! User saved to Supabase.", "name": new_user.full_name}