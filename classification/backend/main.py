import asyncio
from time import perf_counter

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import drivereader.drive as drive
from drivereader.database import fetch_all_folders, fetch_all_files

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

@app.get("/api/folders")
def read_all_folders():
    return fetch_all_folders()

@app.get("/api/files")
def read_all_files():
    return fetch_all_files()

@app.get("/api/files/{code}")
def read_files_by_code(code: str):
    return fetch_all_files({"code": code})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
# print(perf_counter() - time_now)