from typing import Annotated, Any
from datetime import date
from xmlrpc.client import Boolean
from pydantic import BaseModel, ConfigDict

test_list = [
    {"day": 5, "views": 5252, "regs": 21},
    {"day": 6, "views": 7620, "regs": 46},
    {"day": 7, "views": 941, "regs": 9},
    {"day": 8, "views": 1159, "regs": 8},
    {"day": 9, "views": 485, "regs": 3},
    {"day": 10, "views": 299, "regs": 6},
    {"day": 11, "views": 239, "regs": 4},
    {"day": 12, "views": 195, "regs": 2},
    {"day": 13, "views": 181, "regs": 2},
    {"day": 14, "views": 180, "regs": 2},
]


class SDataSetsBase(BaseModel):
    dataset_name: str


class SDataSets(SDataSetsBase):
    model_config = ConfigDict(from_attributes=True)


class SDataSetsCreate(SDataSetsBase):
    dataset: list | str = test_list
    model_config = ConfigDict(from_attributes=True)


class SDataSetsUpdate(SDataSetsBase):
    model_config = ConfigDict(from_attributes=True)


class SModelsBase(BaseModel):
    name_model: str
    type_model: str


class SModels(SModelsBase):
    model_config = ConfigDict(from_attributes=True)
    data_model: bytes


class SModelsView(SModelsBase):
    model_config = ConfigDict(from_attributes=True)


class SModelsShow(SModelsBase):
    model_config = ConfigDict(from_attributes=True)
    created_at: date


class SModelsBaseUpdate(SModelsBase):
    model_config = ConfigDict(from_attributes=True)


class STrainingBase(BaseModel):
    name_model: str
    type_model: str = "linear"


class STrainingCreate(STrainingBase):
    dataset_name: str


class STrainingView(STrainingBase):
    name_model: str
    type_model: str
    task_id: str


class PredictBase(BaseModel):
    name_model: str = "model1"
    dataset_name: str = "dataset1"
