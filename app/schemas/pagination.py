from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


# Offset pagination response
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    has_more: bool


# Cursor pagination response
class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    limit: int
    next_cursor: int | None
    has_more: bool