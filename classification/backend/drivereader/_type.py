from pydantic import BaseModel
from typing import Optional

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