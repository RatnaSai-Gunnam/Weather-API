from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False)
    record_date = Column(Date, nullable=False)
    max_temp = Column(Float)          # degrees C
    min_temp = Column(Float)          # degrees C
    precipitation = Column(Float)     # centimeters

    __table_args__ = (
        UniqueConstraint("station_id", "record_date", name="uq_station_date"),
    )


class WeatherStats(Base):
    __tablename__ = "weather_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    avg_max_temp = Column(Float)
    avg_min_temp = Column(Float)
    total_precipitation = Column(Float)

    __table_args__ = (
        UniqueConstraint("station_id", "year", name="uq_station_year"),
    )


def get_engine(db_url: str = "sqlite:///weather.db"):
    """Return SQLAlchemy engine."""
    return create_engine(db_url, echo=False, future=True)


def get_session(db_url: str = "sqlite:///weather.db"):
    """Return SQLAlchemy session factory."""
    engine = get_engine(db_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return SessionLocal()
