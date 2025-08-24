import os
from sqlalchemy import extract, func, delete
from sqlalchemy.orm import sessionmaker

from schema import WeatherData, WeatherStats, get_engine

DB_URL = os.getenv("DB_URL", "sqlite:///weather.db")


def calculate_yearly_stats():
    """Compute yearly stats per station from WeatherData into WeatherStats."""
    engine = get_engine(DB_URL)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    # Clear existing stats for idempotency
    session.execute(delete(WeatherStats))

    # Aggregate weather data by station and year
    results = session.query(
        WeatherData.station_id.label("station_id"),
        extract("year", WeatherData.record_date).label("year"),
        func.avg(WeatherData.max_temp).label("avg_max_temp"),
        func.avg(WeatherData.min_temp).label("avg_min_temp"),
        func.sum(WeatherData.precipitation).label("total_precipitation"),
    ).group_by(
        WeatherData.station_id, extract("year", WeatherData.record_date)
    ).all()

    # Insert aggregated stats
    for r in results:
        ws = WeatherStats(
            station_id=r.station_id,
            year=int(r.year),
            avg_max_temp=float(r.avg_max_temp) if r.avg_max_temp is not None else None,
            avg_min_temp=float(r.avg_min_temp) if r.avg_min_temp is not None else None,
            total_precipitation=float(r.total_precipitation) if r.total_precipitation is not None else None,
        )
        session.add(ws)

    session.commit()
    session.close()
    print(f"[INFO] Stats calculated for {len(results)} station-year rows.")


if __name__ == "__main__":
    calculate_yearly_stats()
