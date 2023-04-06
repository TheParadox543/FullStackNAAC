from pydantic import BaseModel
from typing import Optional, TypedDict, TypeVar

Category = TypeVar("Category", bound=str)
Classification = TypeVar("Classification", bound=str)
Code = TypeVar("Code", bound=str)
Name = TypeVar("Name", bound=str)
Year = TypeVar("Year", bound=str)

class FileBasic(TypedDict, total=False):
    kind: str
    id: str
    name: str
    mimeType: str

class File(BaseModel):
    kind: str
    id: str
    name: str
    mimeType: str
    description: Optional[str] = None
    trashed: Optional[bool] = None
    parents: Optional[list[str]] = None

class FileList(BaseModel):
    kind: str
    nextPageToken: Optional[str] = None
    incompleteSearch: bool = False
    files: list[File]