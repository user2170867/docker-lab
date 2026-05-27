from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import asyncpg
import databases
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/appdb")
database = databases.Database(DATABASE_URL)

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: str = None

class ItemIn(BaseModel):
    name: str
    description: str = None

@app.on_event("startup")
async def startup():
    await database.connect()
    # create table if not exists
    await database.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "Hello Docker"}

@app.get("/items", response_model=List[Item])
async def get_items():
    rows = await database.fetch_all("SELECT id, name, description FROM items")
    return rows

@app.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemIn):
    query = "INSERT INTO items (name, description) VALUES (:name, :description) RETURNING id, name, description"
    row = await database.fetch_one(query=query, values={"name": item.name, "description": item.description})
    return row
