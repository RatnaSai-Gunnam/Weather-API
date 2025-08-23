import os
from sqlalchemy import extract, func, delete
from sqlalchemy.orm import sessionmaker

from schema import WeatherData, WeatherStats, get_engine

DB_URL = os.getenv("DB_URL", "sqlite:///weather.db")

def calculate_yearly_stats():
    engine = get_engine(DB_URL)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    # Recompute from scratch for idempotency/simplicity
    session.execute(delete(WeatherStats))

    results = session.query(
        WeatherData.station_id.label('station_id'),
        extract('year', WeatherData.record_date).label('year'),
        func.avg(WeatherData.max_temp).label('avg_max'),
        func.avg(WeatherData.min_temp).label('avg_min'),
        func.sum(WeatherData.precipitation).label('total_precip')
    ).group_by(WeatherData.station_id, extract('year', WeatherData.record_date)).all()

    for r in results:
        ws = WeatherStats(
            station_id=r.station_id,
            year=int(r.year),
            avg_max_temp=float(r.avg_max) if r.avg_max is not None else None,
            avg_min_temp=float(r.avg_min) if r.avg_min is not None else None,
            total_precipitation=float(r.total_precip) if r.total_precip is not None else None
        )
        session.add(ws)

    session.commit()
    session.close()
    print(f"[INFO] Stats calculated for {len(results)} station-year rows.")

if __name__ == "__main__":
    calculate_yearly_stats()
