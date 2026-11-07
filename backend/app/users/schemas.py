import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class RegisterIn(BaseModel):
    username: str
    password: str


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    username: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"