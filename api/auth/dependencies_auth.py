from datetime import datetime, timedelta, timezone
import uuid
import bcrypt
import jwt

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2, OAuth2PasswordBearer
from core.models import db_helper
from auth.schemas import RefreshSessionCreate, RefreshSessionUpdate, Token
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param


from core.config import auth_settings
from ds.dependencies import Dependencies
from exception.exceptions import (
    InvalidTokenException,
    InvalidUserName,
    Invalidauthenticated,
    TokenExpiredException,
)
from users.models import RefreshSessionModel, UserModel
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = auth_settings.private_key_path.read_text(),
    algorithm: str = auth_settings.algorithm,
    expire_minutes: int = auth_settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(datetime.UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = auth_settings.public_key_path.read_text(),
    algorithm: str = auth_settings.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str,
) -> str:
    salt = bcrypt.gensalt()
    pwd_str: str = password.encode()
    hash_passw = bcrypt.hashpw(pwd_str, salt).decode("utf-8")
    return hash_passw


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/jwt/login")


class Dependencies_auth:

    # Auth user
    @staticmethod
    async def authenticate_user(
        username: str,
        password: str,
        session: AsyncSession,
    ) -> Optional[UserModel]:
        user_exist = await Dependencies.find_one_or_none(
            session=session, model=UserModel, username=username
        )

        if user_exist and validate_password(
            password, user_exist.password.encode("utf-8")
        ):
            return user_exist
        return None

    @staticmethod
    def create_refresh_token() -> str:
        return uuid.uuid4()

    @staticmethod
    def create_access_token(user_id: uuid.UUID) -> str:
        private_key: str = auth_settings.private_key_path.read_text()
        algorithm: str = auth_settings.algorithm
        jwt_payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow()
            + timedelta(minutes=auth_settings.access_token_expire_minutes),
        }
        encoded_jwt = jwt.encode(jwt_payload, private_key, algorithm=algorithm)
        return encoded_jwt

    @staticmethod
    async def create_token(
        user_id: uuid.UUID,
        session: AsyncSession,
    ) -> Token:
        access_token = Dependencies_auth.create_access_token(user_id)
        refresh_token_expires = timedelta(days=auth_settings.refresh_token_expire_days)
        refresh_token = Dependencies_auth.create_refresh_token()
        # create_item

        dict_params = {
            "model": RefreshSessionModel,
            "value": RefreshSessionCreate(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
            ),
        }
        await Dependencies.create_item(session=session, **dict_params)
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @staticmethod
    async def logout(
        token: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        refresh_session = await Dependencies.find_one_or_none(
            session=session, model=RefreshSessionModel, refresh_token=token
        )
        if refresh_session:
            await Dependencies.delete(
                session=session, model=RefreshSessionModel, id=refresh_session.id
            )
            await session.commit()
        else:
            raise Invalidauthenticated

    @staticmethod
    async def refresh_token(
        token: uuid.UUID,
        session: AsyncSession,
    ) -> Token:
        refresh_session = await Dependencies.find_one_or_none(
            session=session, model=RefreshSessionModel, refresh_token=token
        )
        if refresh_session is None:
            raise InvalidTokenException
        if datetime.now(timezone.utc) >= refresh_session.created_at + timedelta(
            seconds=refresh_session.expires_in
        ):
            await Dependencies.delete(
                session=session, model=RefreshSessionModel, id=refresh_session.id
            )
            raise TokenExpiredException

        user = await Dependencies.find_one_or_none(
            session=session, model=UserModel, id=refresh_session.user_id
        )
        if user is None:
            raise InvalidTokenException

        access_token = Dependencies_auth.create_access_token(user.id)
        refresh_token_expires = timedelta(days=auth_settings.refresh_token_expire_days)
        refresh_token = Dependencies_auth.create_refresh_token()

        await Dependencies.update(
            session=session,
            model=RefreshSessionModel,
            data_in=RefreshSessionUpdate(
                refresh_token=refresh_token,
                expires_in=refresh_token_expires.total_seconds(),
            ),
        )
        await session.commit()
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @staticmethod
    async def abort_all_sessions(
        session: AsyncSession,
        user_id: uuid.UUID,
    ):
        await Dependencies.delete(
            session, RefreshSessionModel, RefreshSessionModel.user_id == user_id
        )
        await session.commit()


async def get_current_user(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    token: str = Depends(oauth2_scheme),
) -> Optional[UserModel]:
    payload = jwt.decode(
        token,
        auth_settings.public_key_path.read_text(),
        algorithms=[auth_settings.algorithm],
    )
    user_id = payload.get("sub")

    dict_params = {
        "model": UserModel,
        "name_param": UserModel.id,
        "value": user_id,
    }
    user_exist = await Dependencies.get_item_to_param(session=session, **dict_params)

    if not user_exist.is_verified:
        raise InvalidUserName
    return user_exist


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
        )
    return current_user
