from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class DefaultResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None
    meta: dict | None

class CreatedResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None

class DefaultError(BaseModel):
    code: str
    message: str
    detail: list | None
    