from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017")
database = client.NAAC
files_data = database.file_data
folders_data = database.folders_data

def fetch_file_document(file_details: dict):
    document = files_data.find_one(file_details)
    return document

def create_file_document(file_details: dict):
    result = files_data.insert_one(file_details)
    document = files_data.find_one({"_id": result.inserted_id})
    return document

def fetch_folder_document(folder_details: dict):
    document = folders_data.find_one(folder_details)
    return document

def create_folder_document(folder_details: dict):
    folder_details["_id"] = folder_details.pop("id")
    try:
        result = folders_data.insert_one(folder_details)
    except DuplicateKeyError as error:
        pass
    document = folders_data.find_one({"_id": folder_details["_id"]})
    return document