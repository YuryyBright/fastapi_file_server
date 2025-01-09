"""Define the Base Schema structures we will inherit from."""
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.examples import ExampleUser
from datetime import datetime

class UserBase(BaseModel):
    """Base for the User Schema."""

    model_config = ConfigDict(from_attributes=True)

    email: str = Field(examples=[ExampleUser.email])


class UserCreate(BaseModel):
    """Base for the User Schema."""
    model_config = ConfigDict(from_attributes=True)
    password: str = Field(examples=[ExampleUser.password])



class LogoutResponse(BaseModel):
    message: str


class SysNodeType(Enum):
    folder = "folder"
    file = "file"

class SysNode(BaseModel):
    name: str
    type: SysNodeType
    mtime: datetime
    ctime: datetime