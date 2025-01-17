from pydantic import BaseModel, Field

class ArchiveRequest(BaseModel):
    """
    Request model for archive creation

    Attributes:
        current_path: Path to the directory to be archived
        archive_name: Name of the output archive file (optional)
    """
    current_path: str
    archive_name: str

    # @validator('archive_name')
    # def validate_archive_name(cls, v):
    #     if not v.endswith('.zip'):
    #         raise ValueError("Archive name must end with .zip")
    #     return v
