from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Person(BaseModel):
    id: int
    name: str
    age: int

DB: list[Person] = [
    Person(id=1, name="Andriya", age=21),
    Person(id=2, name="Hiran", age=21),
    Person(id=3, name="Sam", age=20),
]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/api")
def read_api():
    return DB

@app.get("/api/{item_id}")
def read_api_id(item_id: int):
    for person in DB:
        if person.id == item_id:
            return person
    return "No user with required ID."