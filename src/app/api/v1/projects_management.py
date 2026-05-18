from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...schemas.project import ProjectCreate, ProjectRead
from ...services import project_management

router = APIRouter(tags=["project-management"])


@router.post(
    "/projects",
    response_model=ProjectRead,
    status_code=201,
    summary="Create project",
    description="Create a project owned by an existing active user.",
    responses={400: {"description": "Invalid owner user"}, 422: {"description": "Validation error"}},
)
async def create_project(
    request: Request, project: ProjectCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    return await project_management.create_project(db=db, project=project)


@router.get(
    "/projects/{id}",
    response_model=ProjectRead,
    summary="Get project by id",
    responses={404: {"description": "Project not found"}},
)
async def get_project_by_id(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    return await project_management.get_project_by_id(db=db, id=id)


@router.get(
    "/users/{id}/projects",
    response_model=list[ProjectRead],
    summary="List projects by user id",
    responses={404: {"description": "User not found"}},
)
async def list_user_projects(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> list[dict[str, Any]]:
    return await project_management.get_projects_by_user_id(db=db, user_id=id)
