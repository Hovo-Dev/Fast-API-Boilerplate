from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class ProjectBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=120, examples=["Project Alpha"])]
    description: Annotated[
        str | None,
        Field(min_length=1, max_length=63206, examples=["Internal migration project"], default=None),
    ]


class Project(TimestampSchema, ProjectBase, UUIDSchema, PersistentDeletion):
    owner_user_id: int


class ProjectRead(BaseModel):
    id: int
    owner_user_id: int
    name: Annotated[str, Field(min_length=1, max_length=120, examples=["Project Alpha"])]
    description: Annotated[str | None, Field(default=None, examples=["Internal migration project"])]
    created_at: datetime


class ProjectCreate(ProjectBase):
    model_config = ConfigDict(extra="forbid")

    owner_user_id: int


class ProjectCreateInternal(ProjectCreate):
    pass


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=1, max_length=120, examples=["Project Beta"], default=None)]
    description: Annotated[
        str | None,
        Field(min_length=1, max_length=63206, examples=["Updated description"], default=None),
    ]


class ProjectUpdateInternal(ProjectUpdate):
    updated_at: datetime


class ProjectDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
