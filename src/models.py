from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Satellite(Base):
    __tablename__ = 'satellites'

    # Уникальный номер спутника по каталогу NORAD
    norad_id: Mapped[int] = mapped_column(String(5), primary_key=True) 

    # Название спутника (например, "ISS (ZARYA)")
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Международное обозначение (может быть пустым, поэтому Optional)
    intl_designator: Mapped[Optional[str]] = mapped_column(String(20))

    # Связь с таблицей TLE (один спутник -> много записей TLE в истории)
    tle_history: Mapped[List["TLE_Data"]] = relationship(
        "TLE_Data", back_populates="satellite", cascade="all, delete-orphan"
    )


class TLE_Data(Base):
    __tablename__ = 'tle_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Импортировали и применили ForeignKey
    satellite_id: Mapped[int] = mapped_column(String(5), ForeignKey('satellites.norad_id', ondelete="CASCADE"))
    
    # Время эпохи
    epoch: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Член торможения BSTAR
    bstar: Mapped[float] = mapped_column(Float, nullable=False) 
    
    # Наклонение орбиты (в градусах)
    inclination: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Долгота восходящего узла / RAAN (в градусах)
    raan: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Эксцентриситет
    eccentricity: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Аргумент перигея (в градусах)
    arg_perigee: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Средняя аномалия (в градусах)
    mean_anomaly: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Среднее движение
    mean_motion: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Номер витка в эпоху
    rev_num_at_epoch: Mapped[int] = mapped_column(Integer, nullable=False)

    # Обратная связь со спутником
    satellite: Mapped["Satellite"] = relationship("Satellite", back_populates="tle_history")
    line1: Mapped[str] = mapped_column(String(70), nullable=False)
    line2: Mapped[str] = mapped_column(String(70), nullable=False)


class ObserverStation(Base):  # Заменили Model на Base
    __tablename__ = 'observer_stations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Географические координаты станции наблюдения
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude: Mapped[float] = mapped_column(Float, default=0.0)


class APIKey(Base):
    """API Key model for authentication."""
    __tablename__ = 'api_keys'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)