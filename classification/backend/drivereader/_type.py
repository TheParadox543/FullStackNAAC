from pydantic import BaseModel
from typing import Optional, TypedDict

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