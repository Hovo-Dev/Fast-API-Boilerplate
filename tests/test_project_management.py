from unittest.mock import AsyncMock, patch

import pytest

from src.app.core.exceptions.http_exceptions import BadRequestException, NotFoundException
from src.app.schemas.project import ProjectCreate
from src.app.services import project_management


@pytest.mark.asyncio
async def test_create_project_success(mock_db):
    project = ProjectCreate(owner_user_id=1, name="Project Alpha", description="Description")

    with patch("src.app.services.project_management.crud_users") as mock_users:
        mock_users.get = AsyncMock(return_value={"id": 1})
        with patch("src.app.services.project_management.crud_projects") as mock_projects:
            created = {"id": 10, "owner_user_id": 1, "name": "Project Alpha", "description": "Description"}
            mock_projects.create = AsyncMock(return_value=created)

            result = await project_management.create_project(db=mock_db, project=project)
            assert result == created
            mock_projects.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_project_requires_valid_active_user(mock_db):
    project = ProjectCreate(owner_user_id=999, name="Project Alpha", description=None)

    with patch("src.app.services.project_management.crud_users") as mock_users:
        mock_users.get = AsyncMock(return_value=None)
        with pytest.raises(BadRequestException, match="valid active user_id"):
            await project_management.create_project(db=mock_db, project=project)


@pytest.mark.asyncio
async def test_delete_user_by_id_blocked_if_projects_exist(mock_db):
    with patch("src.app.services.project_management.crud_users") as mock_users:
        mock_users.get = AsyncMock(return_value={"id": 1})
        with patch("src.app.services.project_management.crud_projects") as mock_projects:
            mock_projects.exists = AsyncMock(return_value=True)
            with pytest.raises(BadRequestException, match="cannot be deleted"):
                await project_management.delete_user_by_id(db=mock_db, id=1)


@pytest.mark.asyncio
async def test_delete_user_by_id_success_without_projects(mock_db):
    with patch("src.app.services.project_management.crud_users") as mock_users:
        mock_users.get = AsyncMock(return_value={"id": 1})
        mock_users.delete = AsyncMock(return_value=None)
        with patch("src.app.services.project_management.crud_projects") as mock_projects:
            mock_projects.exists = AsyncMock(return_value=False)
            await project_management.delete_user_by_id(db=mock_db, id=1)
            mock_users.delete.assert_called_once_with(db=mock_db, id=1)


@pytest.mark.asyncio
async def test_get_project_by_id_not_found(mock_db):
    with patch("src.app.services.project_management.crud_projects") as mock_projects:
        mock_projects.get = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException, match="Project not found"):
            await project_management.get_project_by_id(db=mock_db, id=1)
