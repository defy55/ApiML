from datetime import datetime
import uuid
from typing import TYPE_CHECKING, List
import sqlalchemy as sa
from core.models.base import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

# from api_v1 import Route

# if TYPE_CHECKING:
#     from api_v1.routes.models import Route

#     print(Route, "Routeeeeeeee")

# Таблица "Данные" (sensor_data):
#     data_id (PK): идентификатор данных
#     sensor_id (FK): идентификатор датчика, связанный с таблицей "Датчики"
#     data_type: тип данных (уровень загрязнения воздуха, радиационный фон и т.д.)
#     value: значение данных
#     timestamp: временная метка сбора данных


# class StationarySensor(Base):
#     __tablename__ = 'stationary_sensors'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     sensor_id = Column(Integer)
#     sensor_type = Column(String)
#     location = Column(String)
#     # Другие характеристики

# class Route(Base):
#     __tablename__ = 'routes'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     route_id = Column(Integer)
#     start_point = Column(String)
#     end_point = Column(String)
#     creation_time = Column(DateTime)
#     update_time = Column(DateTime)
#     sensor_id = Column(Integer, ForeignKey('mobile_sensors.id'))
#     sensor = relationship("MobileSensor", back_populates="route")
#     base_point = Column(String)
#     district_id = Column(Integer, ForeignKey('districts.id'))
#     district = relationship("District")
#     mobile_sensors = relationship("MobileSensor", back_populates="route")
#     # Другие характеристики

# class MobileSensor(Base):
#     __tablename__ = 'mobile_sensors'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     sensor_id = Column(Integer)
#     sensor_type = Column(String)
#     current_location = Column(String)
#     route_id = Column(Integer, ForeignKey('routes.id'))
#     route = relationship("Route", back_populates="mobile_sensors")
#     # Другие характеристики

# class District(Base):
#     __tablename__ = 'districts'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     district_id = Column(Integer)
#     district_name = Column(String)
#     district_category = Column(String)
#     # Другие характеристики


# class SensorData(Base):
#     __tablename__ = 'sensor_data'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     data_id = Column(Integer)
#     sensor_id = Column(Integer, ForeignKey('stationary_sensors.id'))
#     sensor = relationship("StationarySensor")
#     data_type = Column(String)
#     value = Column(Float)
#     timestamp = Column(DateTime)
#     district_id = Column(Integer, ForeignKey('districts.id'))
#     district = relationship("District")
#     source = Column(String)  # 'stationary' или 'mobile'
#     # Другие характеристики


# sensor_type: тип датчика (стационарный или беспилотный)
# power_source: источник питания (сеть или батарея)
# battery_level: уровень заряда батареи
# is_active: активен ли датчик
# activity_time: время активности для всех датчиков и время полета для подвижных
# error_status: статус ошибки
# signal_level: уровень сигнала канала управления и интернет соединения
# last_update: дата последнего обновления информации от датчика
# (дополнительные поля для подвижных датчиков, такие как маршрут)


# class StationarySensor(Base):
#     __tablename__ = "stationary_sensors"

#     sensor_id: Mapped[int]
#     power_source: Mapped[str] = mapped_column(String(20), nullable=False)
#     is_active: Mapped[bool] = mapped_column(nullable=True)
#     last_update: Mapped[datetime] = mapped_column(nullable=True)
#     location: Mapped[str] = mapped_column(nullable=True)
#     error_status: Mapped[str] = mapped_column(nullable=True)
#     activity_time: Mapped[int] = mapped_column(nullable=True)


# class MobileSensor(Base):
#     __tablename__ = "mobile_sensors"

#     sensor_id = Mapped[int]
#     power_source: Mapped[str] = mapped_column(String(20), nullable=False)
#     battery_level: Mapped[float] = mapped_column(nullable=False)
#     current_location = Mapped[str]
#     is_active: Mapped[bool] = mapped_column(nullable=True)
#     last_update: Mapped[datetime]
#     sensor_id: Mapped[int]
#     location: Mapped[str]
#     error_status: Mapped[str]
#     activity_time: Mapped[str]


###
# route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
# # route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
# routes_mobile: Mapped["Route"] = relationship(back_populates="mobile_sensors")
###
# route_id = Column(Integer, ForeignKey('routes.id'))
# route = relationship("Route", back_populates="mobile_sensors")


# class Parent(Base):
#     __tablename__ = "parent_table"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     children: Mapped[List["Child"]] = relationship(back_populates="parent")
# class Child(Base):
#     __tablename__ = "child_table"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
#     parent: Mapped["Parent"] = relationship(back_populates="children")


##


# class StationarySensor(Base):
#     __tablename__ = 'stationary_sensors'
#     sensor_id = Column(Integer)
#     sensor_type = Column(String)
#     location = Column(String)
#     # Другие характеристики


# class MobileSensor(Base):
#     __tablename__ = 'mobile_sensors'
#     sensor_id = Column(Integer)
#     sensor_type = Column(String)
#     current_location = Column(String)
#     route_id = Column(Integer, ForeignKey('routes.route_id'))
#     route = relationship("Route", back_populates="mobile_sensors")
#     # Другие характеристики


# class District(Base):
#     __tablename__ = 'districts'
#     district_id = Column(Integer)
#     district_name = Column(String)
#     district_category = Column(String)
#     # Другие характеристики

# class Route(Base):
#     __tablename__ = 'routes'
#     route_id = Column(Integer)
#     start_point = Column(String)
#     end_point = Column(String)
#     creation_time = Column(DateTime)
#     update_time = Column(DateTime)
#     sensor_id = Column(Integer, ForeignKey('mobile_sensors.sensor_id'))
#     sensor = relationship("MobileSensor", back_populates="route")
#     base_point = Column(String)
#     district_id = Column(Integer, ForeignKey('districts.district_id'))
#     district = relationship("District")
#     mobile_sensors = relationship("MobileSensor", back_populates="route")
#     # Другие характеристики


# class SensorData(Base):
#     __tablename__ = 'sensor_data'
#     data_id = Column(Integer)
#     sensor_id = Column(Integer, ForeignKey('stationary_sensors.sensor_id' or 'mobile_sensors.sensor_id'))
#     sensor = relationship("StationarySensor" or "MobileSensor")
#     data_type = Column(String)
#     value = Column(Float)
#     timestamp = Column(DateTime)
#     district_id = Column(Integer, ForeignKey('districts.district_id'))
#     district = relationship("District")
#     source = Column(String)  # 'stationary' или 'mobile'
#     # Другие характеристики


# class SensorData(Base):
#     __tablename__ = "sensor_data"
#     # data_id = Column(Integer, primary_key=True)
#     data_id = Column(Integer)
#     # sensor_id = Column(
#     #     Integer,
#     #     ForeignKey("stationary_sensors.sensor_id" or "mobile_sensors.sensor_id"),
#     # )
#     # sensor = relationship("StationarySensor" or "MobileSensor")
#     data_type = Mapped[str]
#     value = Column(Float)
#     timestamp = Column(DateTime)
#     # district_id = Column(Integer, ForeignKey("districts.district_id"))
#     # district = relationship("District")
#     source = Mapped[str]  # 'stationary' или 'mobile'
#     # Другие характеристики

#     # user_id: Mapped[uuid.UUID] = mapped_column(UUID, sa.ForeignKey(
#     #     "user.id", ondelete="CASCADE"))


# class Sensor_data(Base):
#     __tablename__ = "sensor_data"

#     # id: Mapped[int] = mapped_column(primary_key=True)
#     data_id: Mapped[int] = mapped_column()
#     username: Mapped[str] = mapped_column(String(255))
#     full_name: Mapped[str] = mapped_column(String(255))
#     password: Mapped[str] = mapped_column(String(255))
#     accessmenu: Mapped[str] = mapped_column(String(255))
#     accessdb = Column(String(255))
#     dop1 = Column(String(255))
#     dop2 = Column(String(255))
#     dop3 = Column(String(255))
#     activated: Mapped[bool]
#     email: Mapped[str] = mapped_column(String(255))
#     # statususer = Column(Enum(StatusUsers))
#     statususer = Column(String(255))


# class UserModel(Base):
#     __tablename__ = 'user'

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID, primary_key=True, index=True, default=uuid.uuid4)
#     email: Mapped[str] = mapped_column(unique=True, index=True)
#     hashed_password: Mapped[str]
#     fio: Mapped[str]
#     is_active: Mapped[bool] = mapped_column(default=True)
#     is_verified: Mapped[bool] = mapped_column(default=False)
#     is_superuser: Mapped[bool] = mapped_column(default=False)


# class RefreshSessionModel(Base):
#     __tablename__ = 'refresh_session'

#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     refresh_token: Mapped[uuid.UUID] = mapped_column(UUID, index=True)
#     expires_in: Mapped[int]
#     created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True),
#                                                  server_default=func.now())
#     user_id: Mapped[uuid.UUID] = mapped_column(UUID, sa.ForeignKey(
#         "user.id", ondelete="CASCADE"))
