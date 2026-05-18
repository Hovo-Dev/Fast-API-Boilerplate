from fastapi import APIRouter

from .health import router as health_router
from .projects_management import router as projects_management_router
from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(users_router)
router.include_router(projects_management_router)
