from sys import prefix
from typing import Annotated
from users.models import UserModel
from users.schemas import UserSchema, UserSchemaUpdate

from core.models import db_helper
from auth.dependencies_auth import (
    get_current_active_user,
    hash_password,
)

from fastapi import Query, Depends, Path, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from ds.dependencies import Dependencies


router = APIRouter(prefix="/user", tags=["USERS"])


@router.get("/static/", response_model=list[UserSchema])
async def get_users(
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await Dependencies.get_items(session=session, model=UserModel)


@router.post(
    "/create_new_user/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_user(
    user_data_in: UserSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:
    user_exist = await Dependencies.find_one_or_none(
        session=session, model=UserModel, username=user_data_in.username
    )
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    user_data_in.password = hash_password(user_data_in.password)
    dict_params = {
        "model": UserModel,
        "value": user_data_in,
    }
    return await Dependencies.create_item(session=session, **dict_params)


@router.patch("/update/{user_name}/")
async def update_user_data(
    user_update: UserSchemaUpdate,
    user_name: Annotated[str, Path],
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserSchema:
    user_exist = await Dependencies.find_one_or_none(
        session=session, model=UserModel, username=user_name
    )
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user_update.password != None:
        user_update.password = hash_password(user_update.password)

    dict_params = {
        "model": UserModel,
        "item_id": user_name,
        "update": user_update,
        "name_param": UserModel.username,
    }
    return await Dependencies.update_item(session=session, **dict_params)


@router.delete("/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(
    user_name: Annotated[str, Path],
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    dict_params = {
        "model": UserModel,
        "item_id": user_name,
        "name_param": UserModel.username,
    }
    await Dependencies.item_delete(session=session, **dict_params)
