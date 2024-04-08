import uuid
from exception.exceptions import InvalidCredentialsException, Invalidauthenticated
from core.models import db_helper
from users.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings, auth_settings

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
)

from auth.dependencies_auth import (
    Dependencies_auth,
    get_current_active_user,
    get_current_user,
)
from auth.schemas import Token


router = APIRouter(tags=["JWT"])


@router.post("/login")
async def login(
    response: Response,
    credentials: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Token:

    user = await Dependencies_auth.authenticate_user(
        credentials.username, credentials.password, session
    )
    if not user:
        raise InvalidCredentialsException

    token = await Dependencies_auth.create_token(
        user.id,
        session,
    )
    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=auth_settings.access_token_expire_minutes * 60,
        httponly=True,
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=auth_settings.refresh_token_expire_days * 30 * 24 * 60,
        httponly=True,
    )
    return token


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await Dependencies_auth.logout(request.cookies.get("refresh_token"), session)
    return {"message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Token:
    if request.cookies.get("refresh_token") == None:
        raise Invalidauthenticated
    new_token = await Dependencies_auth.refresh_token(
        uuid.UUID(request.cookies.get("refresh_token")),
        session,
    )
    response.set_cookie(
        "access_token",
        new_token.access_token,
        max_age=auth_settings.access_token_expire_minutes * 60,
        httponly=True,
    )
    response.set_cookie(
        "refresh_token",
        new_token.refresh_token,
        max_age=auth_settings.refresh_token_expire_days * 30 * 24 * 60,
        httponly=True,
    )
    return new_token


@router.post("/abort")
async def abort_all_sessions(
    response: Response,
    user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await Dependencies_auth.abort_all_sessions(session, user.id)
    return {"message": "All sessions was aborted"}
