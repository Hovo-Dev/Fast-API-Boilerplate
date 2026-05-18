from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions.http_exceptions import BadRequestException, DuplicateValueException, NotFoundException
from ..crud.crud_projects import crud_projects
from ..crud.crud_users import crud_users
from ..schemas.project import ProjectCreate, ProjectCreateInternal, ProjectRead
from ..schemas.user import UserCreate, UserCreateInternal, UserRead


async def create_user(db: AsyncSession, user: UserCreate) -> dict[str, Any]:
    if await crud_users.exists(db=db, email=user.email):
        raise DuplicateValueException("Email is already registered")

    if await crud_users.exists(db=db, username=user.username):
        raise DuplicateValueException("Username not available")

    user_internal = UserCreateInternal(**user.model_dump())
    created_user = await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)

    if created_user is None:
        raise NotFoundException("Failed to create user")

    return created_user


async def get_user_by_id(db: AsyncSession, id: int) -> dict[str, Any]:
    db_user = await crud_users.get(db=db, id=id, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")
    return db_user


async def delete_user_by_id(db: AsyncSession, id: int) -> None:
    await get_user_by_id(db=db, id=id)
    if await crud_projects.exists(db=db, owner_user_id=id, is_deleted=False):
        raise BadRequestException("This user owns active projects and cannot be deleted")
    await crud_users.delete(db=db, id=id)


async def create_project(db: AsyncSession, project: ProjectCreate) -> dict[str, Any]:
    owner = await crud_users.get(db=db, id=project.owner_user_id, is_deleted=False, schema_to_select=UserRead)
    if owner is None:
        raise BadRequestException("A valid active user_id is required to create a project")

    project_internal = ProjectCreateInternal(**project.model_dump())
    created_project = await crud_projects.create(db=db, object=project_internal, schema_to_select=ProjectRead)

    if created_project is None:
        raise NotFoundException("Failed to create project")

    return created_project


async def get_project_by_id(db: AsyncSession, id: int) -> dict[str, Any]:
    db_project = await crud_projects.get(db=db, id=id, is_deleted=False, schema_to_select=ProjectRead)
    if db_project is None:
        raise NotFoundException("Project not found")
    return db_project


async def get_projects_by_user_id(db: AsyncSession, user_id: int) -> list[dict[str, Any]]:
    await get_user_by_id(db=db, id=user_id)
    projects = await crud_projects.get_multi(db=db, owner_user_id=user_id, is_deleted=False, offset=0, limit=10_000)
    return cast(list[dict[str, Any]], projects["data"])
