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
from typing import Optional, TypeVar, Union

# Import project specific modules.
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from drivereader._type import (
    FileBasic,
    Category,
    Code,
    Name,
    Year,
    CodeList
)
from drivereader.util import sort_dictionary
from drivereader.database import (
    create_folder_document,
    create_file_document,
    create_exempt_document
)

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
            fields="files(id, name, mimeType, webViewLink)"
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

def sort_files():
    service = make_connection()
    with open("data/code_list.json", "r") as code_data:
        code_list = load(code_data)
    try:
        with open("data/folders.json", "r") as file:
            folder_names: list[str] = load(file)
    except FileNotFoundError:
        logger_monitor.exception("Please specify the folders to search in `folders.json`.")
        return None

    folders, files = [], []
    for folder_search in folder_names:
        folder = search_folder(folder_search, service)
        folder = create_folder_document(folder)
        folder_id = folder.get("_id")
        folders.append(folder.get("name"))

        try:
            page_token = None
            while True:
                # Search for all files with the folder as parent.
                response = service.files().list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType)',
                    pageToken=page_token
                ).execute()

                for file in response.get("files"):
                    file: FileBasic
                    if file.get("name") is not None:
                        year, code = file_details_from_name(file.get("name"), code_list)
                        file["parent"] = folder_id
                        if year is not None and code is not None:
                            file["year"] = year
                            file["code"] = code
                            create_file_document(file)
                            files.append(file.get("name"))
                        else:
                            create_exempt_document(file)
                page_token = response.get("nextPageToken", None)

                if page_token is None:
                    break

        except HttpError as error:
            logger_monitor.exception(f"An error occurred: {error}")

    return folders, files

def file_details_from_name(name: str, code_list: CodeList):
    try:
        date, code, _ = name.split("_", 2)
        code = code.upper()
        if code not in code_list:
            raise KeyError
    except ValueError:
        return None, None
    except KeyError:
        return None, None
    else:
        try:
            year, month = int(date[:4]), int(date[4:6])
            # print(year, month, day)
            if month > 0 and month < 5:
                year = f"{year-1}-{year}"
            else:
                year = f"{year}-{year+1}"
        except ValueError:
            return None, None
        else:
            return year, code
