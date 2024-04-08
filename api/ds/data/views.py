import importlib
import io
import json
import re

from fastapi.responses import JSONResponse
from auth.dependencies_auth import get_current_active_user
from users.models import UserModel
from exception.exceptions import DublicatName, InvalidDatasetName
from core.models import db_helper
from ds.dependencies import Dependencies
from .models import DataSets, TrainedModels
from fastapi import Query, Depends, Path, APIRouter, UploadFile
from fastapi_cache.decorator import cache
from sqlalchemy.exc import IntegrityError
import pandas as pd


from ds.data.schemas import (
    PredictBase,
    SDataSets,
    SDataSetsCreate,
    SModelsBase,
    STrainingCreate,
    STrainingView,
)
from fastapi import Query, Depends, Path, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.tasks import AsyncResult

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:


router = APIRouter(tags=["DATASETS/MODELS"])


@router.get("/datasets/")
async def get_all_datasets(
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> list[SDataSets]:
    return await Dependencies.get_items(session=session, model=DataSets)


@router.get("/tasks/{task_id}")
async def get_status(
    task_id: str,
    current_user: UserModel = Depends(get_current_active_user),
):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
    }
    task_status = task_result.status
    if task_status == "FAILURE":
        result.update({"task_status": task_result.status})
    else:
        result.update({"task_status": task_result.status})
        result.update({"task_result": task_result.result})
    return JSONResponse(result)


@router.get("/models/")
async def get_all_models(
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> list[SModelsBase]:
    return await Dependencies.get_items(session=session, model=TrainedModels)


@router.post(
    "/create_dataset/",
    response_model=SDataSetsCreate,
    status_code=status.HTTP_201_CREATED,
)
async def create_dataset(
    data_in: SDataSetsCreate,
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> SDataSetsCreate:
    data_in.dataset = json.dumps(data_in.dataset)
    dict_params = {
        "model": DataSets,
        "value": data_in,
    }
    try:
        return await Dependencies.create_item(session=session, **dict_params)
    except IntegrityError as ex:
        error_message = ex.orig.args[0]
        if "duplicate key value violates" in error_message:
            raise DublicatName


@router.post(
    "/upload_dataset/",
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    dataset_csv_file: UploadFile,
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    contents = await dataset_csv_file.read()
    dataset_json = json.dumps(
        pd.read_csv(io.BytesIO(contents), encoding="utf8").to_dict("records")
    )
    dict_params = {
        "model": DataSets,
        "value": dataset_json,
        "value": SDataSetsCreate(
            dataset_name=re.sub("[^A-Za-z0-9]", "", dataset_csv_file.filename),
            dataset=dataset_json,
        ),
    }

    try:
        return await Dependencies.create_item(session=session, **dict_params)
    except IntegrityError as ex:
        error_message = ex.orig.args[0]
        if "duplicate key value violates" in error_message:
            raise DublicatName
    if not dataset_csv_file:
        return {"Dataset upload": "No upload file sent"}
    else:
        return {"Dataset upload": dataset_csv_file.filename}


@router.post(
    "/training_model/",
    response_model=STrainingView,
    status_code=status.HTTP_201_CREATED,
)
async def training_model(
    data_in: STrainingCreate,
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> STrainingView:
    data_in_json = dict(data_in)
    dataset_exist = await Dependencies.find_one_or_none(
        session=session, model=DataSets, dataset_name=data_in.dataset_name
    )
    name_model_exist = await Dependencies.find_dublicate(
        session=session, model=TrainedModels, name_model=data_in.name_model
    )

    if dataset_exist:
        task = getattr(
            importlib.import_module("tasks.tasks"), "training_model_task"
        ).apply_async(kwargs=(data_in_json), result=True)
        task_id = task.id
    else:
        raise InvalidDatasetName

    return {
        "name_model": f"{data_in.name_model}",
        "type_model": f"{data_in.type_model}",
        "task_id": task_id,
    }


@router.post(
    "/predict/",
)
async def predict(
    data_in: PredictBase,
    current_user: UserModel = Depends(get_current_active_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await Dependencies.predict(session=session, data_in=data_in)
