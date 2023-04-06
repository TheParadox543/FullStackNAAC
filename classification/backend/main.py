import asyncio
import re
from time import perf_counter
from typing import Annotated, Optional

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import drivereader.drive as drive
from drivereader.database import (
    fetch_all_folders,
    fetch_all_files,
    fetch_naac_count
)
from _type import CodeValues

time_now = perf_counter()
app = FastAPI()

origins = ["https://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Ping": "Pong"}

@app.get("/api/naac")
def get_naac_data():
    return fetch_naac_count()

@app.get("/api/folders")
def read_all_folders():
    return fetch_all_folders()

@app.get("/api/files")
def read_all_files(
    code: Annotated[Optional[CodeValues],
        Query(description="The code that needs to be searched for")
    ]=None,
    year: Annotated[str,
        Query(min_length=9, max_length=9,example="2022-2023")
    ]=""
):
    if re.match("\d{4}-\d{4}", year):
        year1, year2 = [int(x) for x in year.split("-")]
        if year2 != year1 + 1:
            year = None
    else:
        year = None
    search = {}
    if code is not None:
        search["code"] = code
    if year is not None:
        search["year"] = year
    return fetch_all_files(search)

# @app.get("/api/files/{code}")
# def read_files_by_code(code: str):
#     return fetch_all_files({"code": code})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
# print(perf_counter() - time_now)