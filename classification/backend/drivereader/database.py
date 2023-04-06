from typing import Optional

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017")
database = client.NAAC
files_data = database.files_data
folders_data = database.folders_data

def fetch_file_document(file_details: dict):
    document = files_data.find_one(file_details)
    return document

def create_file_document(file_details: dict):
    file_details["_id"] = file_details.pop("id")
    try:
        result = files_data.insert_one(file_details)
        inserted_id = result.inserted_id
    except DuplicateKeyError as error:
        inserted_id = error._message.split("\"", 2)[1]
    document = files_data.find_one({"_id": inserted_id})
    return document

def fetch_all_files(filter: Optional[dict]=None):
    files_list = []
    files = files_data.find(filter)
    for file in files:
        files_list.append(file)
    return files_list

def fetch_folder_document(folder_details: dict):
    document = folders_data.find_one(folder_details)
    return document

def create_folder_document(folder_details: dict):
    folder_details["_id"] = folder_details.pop("id")
    try:
        result = folders_data.insert_one(folder_details)
        inserted_id = result.inserted_id
    except DuplicateKeyError as error:
        inserted_id = error._message.split("\"", 2)[1]
    document = folders_data.find_one({"_id": inserted_id})
    return document

def fetch_all_folders():
    folder_list = []
    folders = folders_data.find()
    for folder in folders:
        folder_list.append(folder)
    return folder_list