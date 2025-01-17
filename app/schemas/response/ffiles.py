from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, validator, Field

from app.schemas.base import SysNode, SysNodeType


class SysFolder(SysNode):
    type: SysNodeType = SysNodeType.folder

class SysFile(SysNode):
    type: SysNodeType = SysNodeType.file
    size: str
    mime: Optional[str]


class ArchiveResponse(BaseModel):
    """
    Response model for successful archive creation

    Attributes:
        archive_url: URL to download the created archive
        message: Success message
        created_at: Timestamp of archive creation
        file_count: Number of files archived
    """
    archive_url: str
    message: str
    # created_at: datetime
    # file_count: int


class ErrorResponse(BaseModel):
    """
    Response model for error cases

    Attributes:
        detail: Error message
        error_code: Unique error identifier
    """
    detail: str
    error_code: str = Field(default_factory=lambda: str(uuid4()))