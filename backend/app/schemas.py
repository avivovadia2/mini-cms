"""Pydantic types shared by every module: request field types and the paginated list shape."""

from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, BeforeValidator, EmailStr, Field, StringConstraints

T = TypeVar("T")

# Required text: surrounding whitespace removed, then at least one character left.
RequiredText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
]

# Free text such as a loss description or a rejection reason: required, up to 5,000 characters.
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]


def _blank_to_none(value: object) -> object:
    """An optional field left empty in a form arrives as "" (or spaces): store it as null."""
    if isinstance(value, str) and not value.strip():
        return None
    return value


OptionalText = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None,
    BeforeValidator(_blank_to_none),
]
OptionalEmail = Annotated[EmailStr | None, BeforeValidator(_blank_to_none)]

MAX_PAGE_SIZE = 100


class PageParams(BaseModel):
    """Query parameters of every list endpoint: `?page_number=2&page_size=50`."""

    page_number: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page_number - 1) * self.page_size


class Page(BaseModel, Generic[T]):
    """One page of a list, plus how many items exist in total (for the pager)."""

    results: list[T]
    total_count: int
