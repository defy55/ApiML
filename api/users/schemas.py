from typing import Annotated, Optional
import uuid
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class CreateUser(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    email: EmailStr


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    email: EmailStr | None = None
    password: str
    fio: str
    is_active: bool
    is_verified: bool
    is_superuser: bool


class UserSchema_id(UserSchema):
    id: uuid.UUID


class UserSchemaUpdate(BaseModel):
    model_config = ConfigDict(strict=True)
    email: EmailStr | None = None
    password: str | None = None
    fio: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    is_superuser: bool | None = None


class RefreshSessionCreate(BaseModel):
    refresh_token: uuid.UUID
    expires_in: int
    user_id: uuid.UUID


class RefreshSessionUpdate(RefreshSessionCreate):
    user_id: Optional[uuid.UUID] = Field(None)


class Token(BaseModel):
    access_token: str
    refresh_token: uuid.UUID
    token_type: str
