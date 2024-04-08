from datetime import date
from pydantic import BaseModel, ConfigDict


class SensorInfoBase(BaseModel):
    sensor_id: int
    power_source: str
    is_active: bool
    activity_time: int
    error_status: str
    last_update: date
    location: str


class SensorInfoStatic(SensorInfoBase):
    sensor_id: int
    pass


class SensorInfoStaticUpdate(BaseModel):
    power_source: str | None = None
    is_active: bool | None = None
    activity_time: int | None = None
    error_status: str | None = None
    last_update: date | None = None
    location: str | None = None


class SensorCreateStatic(SensorInfoBase):
    pass


class SensorInfoMobile(SensorInfoBase):
    battery_level: float
    current_location: str
    signal_level: float


class SensorUpdateMobile(SensorInfoBase):
    battery_level: float | None = None
    current_location: str | None = None
    signal_level: float | None = None


class SensorInfo(SensorInfoBase):
    model_config = ConfigDict(from_attributes=True)
    # id: int


class SensorInfoID:
    def __init__(self, sensor_id: int):
        self.sensor_id = sensor_id
