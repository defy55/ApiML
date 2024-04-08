from fastapi.security import HTTPBasic
from users.models import UserModel

from core.models import db_helper

from auth.dependencies_auth import get_current_active_user
from fastapi import (
    Depends,
    APIRouter,
)

from ds.dependencies import Dependencies


router = APIRouter(tags=["GENERATE"])
security = HTTPBasic()


@router.get(
    "/generate_image/",
)
async def generate_image(
    current_user: UserModel = Depends(get_current_active_user),
):
    return await Dependencies.image_gen()
