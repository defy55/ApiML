from fastapi import APIRouter

from .cv.views import router as computer_vision_router
from .data.views import router as data_router

from auth.jwt_auth import router as jwt_auth_router


router = APIRouter()
router.include_router(router=data_router, prefix="/data")
router.include_router(router=computer_vision_router, prefix="/cv")
router.include_router(router=jwt_auth_router, prefix="/jwt")
