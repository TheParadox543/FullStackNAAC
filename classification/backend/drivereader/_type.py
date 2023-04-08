from pydantic import BaseModel
from typing import Union, TypedDict, TypeVar

Category = TypeVar("Category", bound=str)
Classification = TypeVar("Classification", bound=str)
Code = TypeVar("Code", bound=str)
Name = TypeVar("Name", bound=str)
Year = TypeVar("Year", bound=str)

# Category - The name of major types of requirements.
# Classification - The numeric code.
# Code - A 4 letter (sometimes 3) that represents what it is.
# Name - The full name of the previous mentioned.

class CodeList(TypedDict):
    """dict[Code, tuple[Name, Category, list[Classification]]]"""
    Code: tuple[Name, Category, list[Classification]]

class BaseFile(TypedDict):
    id: str
    name: str
    mimeType: str

class FileFull(BaseFile):
    code: str
    year: str
    parent: list[str]

class Folder(BaseFile):
    webViewLink: str

class File(BaseModel):
    kind: str
    id: str
    name: str
    mimeType: str
    description: Union[str, None] = None
    trashed: Union[bool, None] = None
    parents: Union[list[str], None] = None

class FileList(BaseModel):
    kind: str
    nextPageToken: Union[str, None] = None
    incompleteSearch: bool = False
    files: list[File]