from typing import Optional

# MongoDB Driver
import motor.motor_asyncio

from model import Todo

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
database = client.TodoList
collection = database.todo

async def fetch_one_do(title: str) -> Optional[dict]:
    document = await collection.find_one({"title": title})
    return document

async def fetch_all_todos() -> list[Todo]:
    todos:list[Todo] = []
    cursor = collection.find({})
    async for document in cursor:
        todos.append(Todo(**document))
    return todos

async def create_todo(todo: dict) -> dict:
    result = await collection.insert_one(todo)
    doc = await collection.find_one({"_id": result.inserted_id})
    return doc

async def update_todo(title: str, description:str) -> dict:
    result = await collection.update_one({
        "title": title
    }, {
        "$set": {
            "description": description
        }
    })
    document = await collection.find_one({"title": title})
    return document

async def remove_todo(title: str) -> bool:
    result = await collection.delete_one({"title": title})
    return result.deleted_count