from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
database = client.NAAC
files_data = database.file_data

async def fetch_one_document(file_det: dict):
    document = await files_data.find_one(file_det)
    return document

async def create_file_document(file_det: dict):
    result = await files_data.create_one(file_det)
    document = await files_data.find_one({"_id": result.inserted_id})
    return document

