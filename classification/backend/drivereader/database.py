from json import load
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017")
database = client.NAAC
files_data = database.files_data
folders_data = database.folders_data
exempt_data = database.exempt_data

with open("data/category_list.json", "r") as cat_data:
    categories = load(cat_data)
with open("data/code_list.json", "r") as code_data:
    code_list = load(code_data)

def fetch_file_document(file_details: dict):
    document = files_data.find_one(file_details)
    return document

def create_file_document(file_details: dict):
    key = {"_id": file_details.pop("id")}
    files_data.update_one(
        key,
        {"$set": file_details},
        True
    )
    return files_data.find_one(key)

def create_exempt_document(file_details: dict):
    key = {"_id": file_details.pop("id")}
    exempt_data.update_one(
        key,
        {"$set": file_details},
        True
    )
    return exempt_data.find_one(key)

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
    key = {"_id": folder_details.pop("id")}
    result = folders_data.update_one(
        key,
        {"$set": folder_details},
        True
    )
    document = folders_data.find_one(key)
    return document

def fetch_all_folders():
    folder_list = []
    folders = folders_data.find()
    for folder in folders:
        folder_list.append(folder)
    return folder_list