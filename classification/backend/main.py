import asyncio
import re
from time import perf_counter
from typing import Annotated, Union

import uvicorn
from fastapi import HTTPException, FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from _type import CodeValues
from drivereader.drive import scan_drive, upload_file_to_drive
from drivereader.database import (
    fetch_all_folders,
    fetch_all_files,
    fetch_naac_count,
    get_valid_years
)
from drivereader.excel import ExcelWorker

time_now = perf_counter()
app = FastAPI()

origins = ["https://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["utility"])
def read_root():
    """Test if the backend works.

    Returns
    --
    - JSON
    """
    return {"Ping": "Pong"}

@app.get("/api/refresh", tags=["utility"])
def refresh_drive_data():
    """Rescan all documents in the drive and update data.

    Update the data in the database if there is any change to the file
    names in drive.

    Returns
    ---
    - JSON[str, int]: The count of files the program has scanned
    """
    return scan_drive()

@app.get("/api/naac", tags=["NAAC"])
def get_naac_data(year: Union[str, None]=None):
    """Get the naac related data.

    Returns
    ------
    - JSON: The data that needs to be shown in the site.
    """
    start_year, end_year = select_years(year)
    return fetch_naac_count(start_year, end_year)

@app.get("/api/read_sheet", tags=["drive"])
def read_sheet():
    excel = ExcelWorker()
    return excel.code_list

@app.get("/api/folders", tags=["drive"])
def read_all_folders():
    return fetch_all_folders()

@app.get("/api/sort", tags=["utility"])
def sort_years():
    return get_valid_years()

@app.get("/api/files", tags=["data"])
def read_all_files(
    code: Annotated[Union[str, None],
        Query(description="The code that needs to be searched for")
    ]=None,
    year: Annotated[str,
        Query(min_length=4, max_length=9,example="2022-2023")
    ]=""
):
    start_year, end_year = select_years(year)
    return fetch_all_files(code, start_year, end_year)

@app.post("/api/read-file", tags=["utility"])
async def create_file(file: UploadFile):
    return {"file_size": await file.read()}

@app.post("/api/upload-file", tags=["upload"])
async def upload_file_from_client(file: UploadFile):
    # with open(f"data/{file.filename}", "wb") as buffer:
    #     buffer.write(await file.read())
    return await upload_file_to_drive(file)
    return {"filename": file.filename}

def select_years(year: Union[str, None]=None):
    min_year, max_year = get_valid_years()
    if year is None:
        return min_year, max_year
    years = [int(x) for x in re.findall("\d{4}", year)]
    if len(years) == 1:
        start_year, end_year = years[0], years[0]
    else:
        start_year, end_year = years[0], years[1]
    return start_year, end_year

# @app.get("/api/files/{code}")
# def read_files_by_code(code: str):
#     return fetch_all_files({"code": code})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
# print(perf_counter() - time_now)