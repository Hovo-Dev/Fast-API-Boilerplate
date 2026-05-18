from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...schemas.project import ProjectCreate, ProjectRead
from ...services import project_management

router = APIRouter(tags=["project-management"])


@router.post("/projects", response_model=ProjectRead, status_code=201)
async def create_project(
    request: Request, project: ProjectCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    return await project_management.create_project(db=db, project=project)


@router.get("/projects/{id}", response_model=ProjectRead)
async def get_project_by_id(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    return await project_management.get_project_by_id(db=db, id=id)


@router.get("/users/{id}/projects", response_model=list[ProjectRead])
async def list_user_projects(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> list[dict[str, Any]]:
    return await project_management.get_projects_by_user_id(db=db, user_id=id)
