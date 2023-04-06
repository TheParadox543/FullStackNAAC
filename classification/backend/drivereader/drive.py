# Install necessary libraries with pip install -r requirements.txt
from __future__ import print_function

# Import in-built modules.
import logging
from io import BytesIO
from json import dumps, load
from os import path, remove
from os import system
from pprint import PrettyPrinter
from sys import exit
from typing import Optional, TypeVar

# Import project specific modules.
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from drivereader.excel import ExcelWorker
from drivereader._type import (
    FileBasic,
    Category,
    Code,
    Name,
    Year
)
from drivereader.util import sort_dictionary

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

# Using the logs.
logger_monitor = logging.getLogger(__name__)
logger_monitor.setLevel(logging.ERROR)
handler = logging.FileHandler("drive_reader_logs.log")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger_monitor.addHandler(handler)

EXCEL = ExcelWorker()

def make_connection() -> Optional[Resource]:
    """Provide service to connect with the drive."""
    credentials = None
    if path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not credentials or not credentials.valid:
        refresh = False
        if (credentials and credentials.expired
                and credentials.refresh_token):
            try:
                credentials.refresh(Request())
            except RefreshError:
                remove("token.json")
            else:
                refresh = True
        if refresh is False:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
            except FileNotFoundError:
                print("Credential file not found.")
                return None
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    # Create a connection with drive.
    service = build("drive", "v3", credentials=credentials)
    return service

def search_file_by_name(file_name: str, service=None) -> Optional[FileBasic]:
    """Search for a specific file."""
    if service is None:
        service = make_connection()
        if service is None:
            return
    try:
        response = service.files().list(
            q=f"name contains '{file_name}'"
        ).execute()
        files = response.get("files", None)
        if files is not None and len(files) != 0:
            return files[0]
        else: return None

    except HttpError as error:
        logger_monitor.exception(f"An error occurred: {error}")
        return None

def search_folder(category_name: str, service=None) -> FileBasic:
    """Search for a specific folder."""
    if service is None:
        service = make_connection()
        if service is None:
            return None
    try:
        response = service.files().list(
            q=f"name contains '{category_name}' and mimeType = \
                'application/vnd.google-apps.folder'",
            fields="files(name, id)"
        ).execute()
        folders = response.get("files", None)
        if len(folders) > 0:
            return folders[0]
        else: return None

    except HttpError as error:
        logger_monitor.exception(f"An error occurred: {error}")
        return None

def download_classification_sheet():
    """Download the required excel sheet."""
    service = make_connection()
    EXCEL_SHEET_ID = "1b5yJfOIWCHXdr7VbFxoNLs_SI5zPR7CL0MsCI1zqWaM"
    try:
        mime_type = "application/vnd.openxmlformats-officedocument"
        mime_type += ".spreadsheetml.sheet"
        request = service.files().export_media(fileId=EXCEL_SHEET_ID,
                                                    mimeType=mime_type)
        _file = BytesIO()
        downloader = MediaIoBaseDownload(_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger_monitor.info(F'Download {int(status.progress() * 100)}%.')

        while True:
            try:
                with open("data/doc_classification.xlsx", "wb") as write_file:
                    write_file.write(_file.getbuffer())
            except PermissionError:
                system("taskkill /im EXCEL.EXE naac.xlsx")
            except FileNotFoundError:
                system("MKDIR data")
            else:
                return True

    except HttpError as error:
        logger_monitor.exception(f"{error} has occurred.")
    return False

def categorize_files():
    """Categorize the files in the various folders according to code."""
    service =  make_connection()
    categories = EXCEL.classification_list.values()
    try:
        with open("data/folders.json", "r") as _file:
            folder_names: list[str] = load(_file)
    except FileNotFoundError:
        logger_monitor.exception("Please specify the folders to search in `folders.json`.")
        data = None
        return

    data: dict[Category, dict[Year, dict[Code, int]]] = {
        i: {
            "0": {
                "0": 0
            }
        } for i in categories}
    exempt: list[tuple[Name, str]] = []

    for folder_search in folder_names:
        folder = search_folder(folder_search, service)
        folder_id, folder_name = folder.get("id"), folder.get("name")
        try:
            page_token = None
            while True:
                # Search for all files with the folder as parent.
                response = service.files().list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    spaces='drive',
                    fields='nextPageToken, files(name)',
                    pageToken=page_token
                ).execute()

                for _file in response.get("files"):
                    logger_monitor.info(_file)
                    if _file.get("name") is not None:
                        if_failed = classify_file(_file.get("name"), data)
                        if if_failed:
                            exempt.append((if_failed, folder_name))
                page_token = response.get("nextPageToken", None)

                if page_token is None:
                    break

        except HttpError as error:
            logger_monitor.exception(f"An error occurred: {error}")

    else:
        for category in list(data.keys()):
            while "0" in data[category]:
                del data[category]["0"]
            for year, year_data in data[category].items():
                while "0" in year_data:
                    del year_data["0"]
                data[category][year] = sort_dictionary(year_data)
            data[category] = sort_dictionary(data[category], True)
            if "0" in data[category]:
                data.pop(category)

def classify_file(name:str, data):
    """Classify the file in categories based on naming structure."""
    code_list = EXCEL.code_list
    try:
        date, code, extra = name.split("_", 2)
        code = code.upper()
        if code not in code_list:
            raise KeyError
    except ValueError:
        return name
    except KeyError:
        return name
    else:
        try:
            year, month = int(date[:4]), int(date[4:6])
            # print(year, month, day)
            if month > 0 and month < 5:
                year = f"{year-1}-{year}"
            else:
                year = f"{year}-{year+1}"
        except ValueError:
            return name
        else:
            category = code_list[code][1]
            category_data = data.get(category, {"0": {"0": 0}})
            year_data = category_data.get(year, {"0": 0})
            code_val = year_data.get(code, 0)
            year_data.update({code: code_val + 1})
            category_data.update({year: year_data})
            data.update({category: category_data})

# def main():
#     """The main function of DriveReader class."""
#     download_sheet()
#     excelWorker = ExcelWorker()
#     code_list = excelWorker.code_list
#     categories = excelWorker.classification_list.values()
#     categorize_files()
#     if data is not None:
#         with open("data/data.json", "w") as file:
#             data_obj = dumps(data, indent=4)
#             _file.write(data_obj)
#         with open("data/exempt.json", "w") as file:
#             exempt_obj = dumps(exempt, indent=4)
#             _file.write(exempt_obj)
#         excelWorker.write_data_to_excel(data, exempt)
#         excelWorker.write_naac_data_to_excel(data)

if __name__ == "__main__":
    print(make_connection())