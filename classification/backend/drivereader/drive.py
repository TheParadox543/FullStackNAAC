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
from drivereader._type import FileBasic

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

pp = PrettyPrinter(indent=4)

# Using the logs.
logger_monitor = logging.getLogger(__name__)
logger_monitor.setLevel(logging.ERROR)
handler = logging.FileHandler("drive_reader_logs.log")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger_monitor.addHandler(handler)

# * Declare a few types to help with understanding.
Category = TypeVar("Category", bound=str)
Classification = TypeVar("Classification", bound=str)
Code = TypeVar("Code", bound=str)
Name = TypeVar("Name", bound=str)
Year = TypeVar("Year", bound=str)

def sort_dictionary(unsorted_dict: dict[str, ], reverse=False):
    """A util function to sort the keys of a dictionary.

    Parameters
    ---------
    - unsorted_dict`dict[str, Any]`: The dictionary that needs to be sorted.
    - reverse`bool`: Whether the keys need to be sorted in reverse order.

    Returns
    ------
    - sorted_dict`dict[str, Any]`: The dictionary with keys sorted.
    """
    order_list: list[str] = sorted(unsorted_dict.keys(), reverse=reverse)
    sorted_dictionary = {i: unsorted_dict[i] for i in order_list}
    return sorted_dictionary

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

        try:
            while True:
                    break

        except HttpError as error:

    def categorize_files(self):
        """Categorize the files in the various folders according to code."""
        try:
            with open("data/folders.json", "r") as file:
                folder_names: list[str] = load(file)
        except FileNotFoundError:
            logger_monitor("Please specify the folders to search in `folders.json`.")
            self.data = None
            return

        self.data: dict[Category, dict[Year, dict[Code, int]]] = {
            i: {
                "0": {
                    "0": 0
                }
            } for i in self.categories}
        self.exempt: list[tuple[Name, str]] = []

        for folder_search in folder_names:
            folder = self.search_folder(folder_search)
            folder_id, folder_name = folder.get("id"), folder.get("name")
            try:
                page_token = None
                while True:
                    # Search for all files with the folder as parent.
                    response = self.service.files().list(
                        q=f"'{folder_id}' in parents and trashed = false",
                        spaces='drive',
                        fields='nextPageToken, files(name)',
                        pageToken=page_token
                    ).execute()

                    for file in response.get("files"):
                        # logger_monitor(file)
                        if file.get("name") is not None:
                            if_failed = self.classify_file(file.get("name"))
                            if if_failed:
                                self.exempt.append((if_failed, folder_name))
                    page_token = response.get("nextPageToken", None)

                    if page_token is None:
                        break

            except HttpError as error:
                logger_monitor(f"An error occurred: {error}")

        else:
            for category in list(self.data.keys()):
                while "0" in self.data[category]:
                    del self.data[category]["0"]
                for year, year_data in self.data[category].items():
                    while "0" in year_data:
                        del year_data["0"]
                    self.data[category][year] = sort_dictionary(year_data)
                self.data[category] = sort_dictionary(self.data[category], True)
                if "0" in self.data[category]:
                    self.data.pop(category)

    def classify_file(self, name:str):
        """Classify the file in categories based on naming structure."""
            logger_monitor.exception(f"An error occurred: {error}")
        try:
            date, code, extra = name.split("_", 2)
            code = code.upper()
            if code not in self.code_list:
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
                category = self.code_list[code][1]
                category_data = self.data.get(category, {"0": {"0": 0}})
                year_data = category_data.get(year, {"0": 0})
                code_val = year_data.get(code, 0)
                year_data.update({code: code_val + 1})
                category_data.update({year: year_data})
                self.data.update({category: category_data})

    def main(self):
        """The main function of DriveReader class."""
        self.download_sheet()
        self.excelWorker = ExcelWorker()
        self.code_list = self.excelWorker.code_list
        self.categories = self.excelWorker.classification_list.values()
        self.categorize_files()
        if self.data is not None:
            with open("data/data.json", "w") as file:
                data_obj = dumps(self.data, indent=4)
                file.write(data_obj)
            with open("data/exempt.json", "w") as file:
                exempt_obj = dumps(self.exempt, indent=4)
                file.write(exempt_obj)
            self.excelWorker.write_data_to_excel(self.data, self.exempt)
            self.excelWorker.write_naac_data_to_excel(self.data)


if __name__ == "__main__":
    # Driver Code
    try:
        DR = DriveReader()
        if DR.credentials and DR.credentials.valid:
            DR.main()
        else:
            print("Could not run the program due to invalid credentials.")
            print("Fix credentials and try again.")
            exit()
    except KeyboardInterrupt:
        print("\n\nExiting program by interrupt.")