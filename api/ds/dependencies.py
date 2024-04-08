import io
import json
import pickle
import importlib
from typing import Annotated, Any, Dict, Optional, TypeVar, Union
from fastapi.responses import StreamingResponse, FileResponse
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

import numpy as np

from fastapi import Path, Depends, HTTPException, status
from pydantic import BaseModel

from ds.data.models import DataSets, TrainedModels
from ds.data.schemas import PredictBase
from exception.exceptions import (
    DublicatName,
    InvalidDatasetModelName,
)


from sqlalchemy import select, delete, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Dependencies:

    @staticmethod
    async def get_items(session: AsyncSession, model: Base):

        stmt = select(model).order_by(model.id)
        result: Result = await session.execute(stmt)
        products = result.scalars().all()
        return products

    # Read one
    @staticmethod
    async def get_item_to_param(
        session: AsyncSession, model: Base, name_param: Any, value: Any
    ):
        stmt = select(model).where(name_param == value)
        result: Result = await session.execute(stmt)
        item = result.scalar()
        if item is not None:
            return item

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Value {value} not found!",
        )

    @staticmethod
    async def find_one_or_none(
        session: AsyncSession, model: Any, **filter_by
    ) -> Optional[ModelType]:
        stmt = select(model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @staticmethod
    async def find_dublicate(
        session: AsyncSession, model: Any, **filter_by
    ) -> Optional[ModelType]:
        stmt = select(model).filter_by(**filter_by)
        answ = await session.execute(stmt)
        result = answ.scalars().one_or_none()
        if result:
            raise DublicatName

    # Create
    @staticmethod
    async def create_item(
        session: AsyncSession,
        model: Base,
        value: Any,
    ):
        if isinstance(value, dict):
            create_data = value
            session.add(**create_data)
        else:
            create_data = model(**value.model_dump())
            session.add(create_data)
        await session.commit()
        # await session.refresh(product)
        return create_data

    # Update
    @staticmethod
    async def update_item(
        model: Base,
        update: Any,
        item_id: Any,
        session: AsyncSession,
        name_param: Any,
        partial: bool = False,
        partial_none: bool = True,
    ):
        item_data = await Dependencies.get_item_to_param(
            session=session, model=model, name_param=name_param, value=item_id
        )
        for name, value in update.model_dump(
            exclude_unset=partial, exclude_none=partial_none
        ).items():
            setattr(item_data, name, value)
        await session.commit()
        return item_data

    @staticmethod
    async def update(
        session: AsyncSession,
        model: Any,
        *where,
        data_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        if isinstance(data_in, dict):
            update_data = data_in
        else:
            update_data = data_in.model_dump(exclude_unset=True)

        stmt = update(model).where(*where).values(**update_data).returning(model)
        result = await session.execute(stmt)
        products = result.scalars().all()
        return products

    # Delete
    @staticmethod
    async def item_delete(
        model: Base,
        item_id: Any,
        name_param: Any,
        session: AsyncSession,
    ) -> None:
        stmt = (
            delete(model)
            .where(name_param == item_id)
            .returning(
                name_param,
            )
        )
        result: Result = await session.execute(stmt)

        item = result.all()
        if item:
            return await session.commit()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Value {item_id} not found!",
        )

    @staticmethod
    async def delete(session: AsyncSession, model, *filter, **filter_by) -> None:
        stmt = delete(model).filter(*filter).filter_by(**filter_by)
        await session.execute(stmt)

    @staticmethod
    async def predict(
        data_in: PredictBase,
        session: AsyncSession,
    ) -> None:
        dataset_exist = await Dependencies.find_one_or_none(
            session=session, model=DataSets, dataset_name=data_in.dataset_name
        )
        model_exist = await Dependencies.find_one_or_none(
            session=session, model=TrainedModels, name_model=data_in.name_model
        )

        if not dataset_exist or not model_exist:
            raise InvalidDatasetModelName

        data_model = pickle.loads(model_exist.data_model)
        data_dataset = dataset_exist.dataset
        data_dataset = pd.json_normalize(json.loads(data_dataset))
        x = data_dataset.views
        y = data_dataset.regs
        LR = data_model.predict(x.values.reshape(-1, 1))
        plt.title("Linear Regression")
        plt.scatter(
            data_dataset.views,
            data_dataset.regs,
            c="red",
            s=25,
            label="Data from dataset",
        )
        plt.plot(x, LR, "g")
        plt.grid()
        plt.xlabel("Views")
        plt.ylabel("Registrations")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        return StreamingResponse(io.BytesIO(buf.read()), media_type="image/png")

    @staticmethod
    def display_image(image):
        torchvision = importlib.import_module("torchvision")
        image_numpy = torchvision.utils.make_grid(image).permute(1, 2, 0).cpu().numpy()
        img = Image.fromarray((image_numpy * 255).astype(np.uint8))
        return img

    @staticmethod
    async def image_gen() -> StreamingResponse:
        torch = importlib.import_module("torch")
        use_gpu = True if torch.cuda.is_available() else False
        model = torch.hub.load(
            "facebookresearch/pytorch_GAN_zoo:hub",
            "PGAN",
            pretrained=True,
            useGPU=use_gpu,
        )
        num_images = 2
        noise, _ = model.buildNoiseData(num_images)
        with torch.no_grad():
            generated_images = model.test(noise)
        result_img = Dependencies.display_image(generated_images)

        combined_buffer = io.BytesIO()
        result_img.save(combined_buffer, format="PNG")
        combined_buffer.seek(0)

        return StreamingResponse(
            io.BytesIO(combined_buffer.getvalue()), media_type="image/png"
        )
