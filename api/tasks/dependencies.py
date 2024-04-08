import json
import pickle
from typing import Annotated, Any, Dict, Optional, TypeVar, Union

import numpy as np
import pandas as pd
from sklearn import linear_model
from sqlalchemy.ext.asyncio import AsyncSession

from ds.data.models import DataSets, TrainedModels
from ds.data.schemas import SModels
from ds.dependencies import Dependencies
from core.models.base import Base
from core.models import db_helper

ModelType = TypeVar("ModelType", bound=Base)


class DependenciesTask:

    @staticmethod
    async def save_trained_model(
        data_in,
        session: AsyncSession = db_helper.get_scoped_session(),
    ) -> None:
        dataset_data = data_in["dataset_name"]
        type_model = data_in["type_model"]
        dataset = await Dependencies.get_item_to_param(
            session=session,
            model=DataSets,
            name_param=DataSets.dataset_name,
            value=dataset_data,
        )
        dataset = json.loads(dataset.dataset)
        data = pd.json_normalize(dataset)

        if type_model == "linear":
            model = linear_model.LinearRegression()
            x = data.views
            y = data.regs
            model.fit(x.values.reshape(-1, 1), y.values.reshape(-1, 1))
            serialized_model = pickle.dumps(model)

        dict_params = {
            "model": TrainedModels,
            "value": SModels(
                name_model=data_in["name_model"],
                type_model=data_in["type_model"],
                data_model=serialized_model,
            ),
        }
        await Dependencies.create_item(session=session, **dict_params)
