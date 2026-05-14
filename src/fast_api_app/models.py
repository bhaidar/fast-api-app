from datetime import UTC, datetime
from typing import Annotated

from pydantic import StringConstraints
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


ProjectName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2),
]


def utc_now() -> datetime:
    return datetime.now(UTC)


class ProjectBase(SQLModel):
    name: ProjectName = Field(unique=True)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class ProjectRead(SQLModel):
    id: int
    name: ProjectName
    slug: str | None = None
    created_at: datetime


class ProjectUpdate(SQLModel):
    name: ProjectName | None = None
    description: str | None = None
    slug: str | None = None
