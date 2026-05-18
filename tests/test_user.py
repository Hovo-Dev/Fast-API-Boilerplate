"""Unit tests for simplified user API endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.users import erase_user_by_id, read_user_by_id, read_users, write_user
from src.app.schemas.user import UserCreate


class TestWriteUser:
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db, sample_user_data, sample_user_read):
        user_create = UserCreate(**sample_user_data)

        with patch("src.app.api.v1.users.project_management.create_user", new_callable=AsyncMock) as create_user:
            create_user.return_value = sample_user_read.model_dump()
            result = await write_user(Mock(), user_create, mock_db)
            assert result == sample_user_read.model_dump()
            create_user.assert_called_once_with(db=mock_db, user=user_create)


class TestReadUsers:
    @pytest.mark.asyncio
    async def test_read_users_success(self, mock_db):
        mock_users_data = {"data": [{"id": 1}, {"id": 2}], "count": 2}

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.get_multi = AsyncMock(return_value=mock_users_data)

            with patch("src.app.api.v1.users.paginated_response") as mock_paginated:
                expected_response = {"data": [{"id": 1}, {"id": 2}], "pagination": {}}
                mock_paginated.return_value = expected_response

                result = await read_users(Mock(), mock_db, limit=10, offset=0)

                assert result == expected_response
                mock_crud.get_multi.assert_called_once()
                mock_paginated.assert_called_once()


class TestReadUserById:
    @pytest.mark.asyncio
    async def test_read_user_by_id_success(self, mock_db, sample_user_read):
        with patch("src.app.api.v1.users.project_management.get_user_by_id", new_callable=AsyncMock) as get_by_id:
            get_by_id.return_value = sample_user_read.model_dump()
            result = await read_user_by_id(Mock(), 1, mock_db)
            assert result == sample_user_read.model_dump()
            get_by_id.assert_called_once_with(db=mock_db, id=1)


class TestEraseUserById:
    @pytest.mark.asyncio
    async def test_erase_user_by_id_success(self, mock_db):
        with patch("src.app.api.v1.users.project_management.delete_user_by_id", new_callable=AsyncMock) as delete_user:
            result = await erase_user_by_id(Mock(), 1, mock_db)
            assert result == {"message": "User deleted"}
            delete_user.assert_called_once_with(db=mock_db, id=1)
