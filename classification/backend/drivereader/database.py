from json import load
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017")
database = client.NAAC
files_data = database.files_data
folders_data = database.folders_data
exempt_data = database.exempt_data
code_collection = database.code_collection

with open("data/category_list.json", "r") as cat_info:
    CATEGORIES = load(cat_info)
with open("data/code_list.json", "r") as code_info:
    CODE_LIST = load(code_info)


def fetch_naac_count():
    result = files_data.aggregate([
        {
            '$match': {
                'year': '2021-2022'
            }
        }, {
            '$group': {
                '_id': '$code',
                'count': {
                    '$count': {}
                }
            }
        }
    ])
    files = {}
    for file in result:
        for code in CODE_LIST[file["_id"]][2]:
            c = files.get(code, 0)
            files[code] = c + file["count"]
    return files

def fetch_file_document(file_details: dict):
    document = files_data.find_one(file_details)
    return document

def fetch_all_files(code: Optional[str], start_year: int, end_year: int):
    files_list = {}
    filter = {}
    for year in range(start_year, end_year+1):
        filter["year"] = year
        if code is not None:
            filter["code"] = code
        files = files_data.find(filter)
        year_data = []
        for file in files:
            file["code"] = CODE_LIST[file.pop("code")][0]
            file.pop("_id")
            file.pop("parent")
            year_data.append(file)
        files_list[year] = year_data
    return files_list

def get_valid_years() -> tuple[int, int]:
    """Get the valid years searches can happen."""
    result = files_data.aggregate([
        {
            '$group': {
                '_id': None,
                'minValue': {
                    '$min': "$year"
                },
                "maxValue": {
                    "$max": "$year"
                }
            }
        }
    ])
    result = next(result, None)
    return result.get("minValue"), result.get("maxValue")

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

def fetch_folder_document(folder_details: dict):
    document = folders_data.find_one(folder_details)
    return document

def fetch_all_folders():
    folder_list = []
    folders = folders_data.find()
    for folder in folders:
        folder_list.append(folder)
    return folder_list

def create_folder_document(folder_details: dict):
    key = {"_id": folder_details.pop("id")}
    folders_data.update_one(
        key,
        {"$set": folder_details},
        True
    )
    document = folders_data.find_one(key)
    return document

def code_insert(code: str, values: tuple[str, str, list[str]], /):
    code_collection.update_one({
        "_id": code
    }, {
        "$set": {
            "name": values[0],
            "category": values[1],
            "classifications": values[2]
        }
    }, True
    )