from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastcrud import PaginatedListResponse, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_users import crud_users
from ...schemas.user import UserCreate, UserRead
from ...services import project_management

router = APIRouter(tags=["users"])


@router.post(
    "/users",
    response_model=UserRead,
    status_code=201,
    summary="Create user",
    description="Create a new user with unique email and username.",
    responses={422: {"description": "Validation or duplicate value error"}},
)
async def write_user(
    request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    return await project_management.create_user(db=db, user=user)


@router.get(
    "/users",
    response_model=PaginatedListResponse[UserRead],
    summary="List users",
    description="List users using limit/offset pagination.",
    responses={422: {"description": "Invalid pagination parameters"}},
)
async def read_users(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    users_data = await crud_users.get_multi(db=db, offset=offset, limit=limit, is_deleted=False)
    page = (offset // limit) + 1
    return paginated_response(crud_data=users_data, page=page, items_per_page=limit)


@router.get(
    "/users/{id}",
    response_model=UserRead,
    summary="Get user by id",
    responses={404: {"description": "User not found"}},
)
async def read_user_by_id(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    return await project_management.get_user_by_id(db=db, id=id)


@router.delete(
    "/users/{id}",
    summary="Delete user by id",
    description="Delete a user only when they do not own active projects.",
    responses={
        400: {"description": "User owns active projects"},
        404: {"description": "User not found"},
    },
)
async def erase_user_by_id(
    request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    await project_management.delete_user_by_id(db=db, id=id)
    return {"message": "User deleted"}
