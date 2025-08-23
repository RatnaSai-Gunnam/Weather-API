import os
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert

from schema import Base, WeatherData, get_engine

DB_URL = os.getenv("DB_URL", "sqlite:///weather.db")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_tables():
    engine = get_engine(DB_URL)
    Base.metadata.create_all(engine)


def _normalize_row(row):
    """Convert raw row values into normalized units with None for missing values."""
    date = pd.to_datetime(str(int(row['date'])), format="%Y%m%d").date()

    def clean(v, div):
        if pd.isna(v) or int(v) == -9999:
            return None
        return float(v) / div

    max_c = clean(row['max'], 10.0)   # tenths °C → °C
    min_c = clean(row['min'], 10.0)
    precip_cm = clean(row['precip'], 100.0)  # tenths mm → cm
    return date, max_c, min_c, precip_cm


def batch_upsert(session, table, records, batch_size=200):
    """Insert records in batches with SQLite ON CONFLICT DO UPDATE."""
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        stmt = insert(table).values(batch)
        stmt = stmt.on_conflict_do_update(
            index_elements=['station_id', 'record_date'],
            set_={
                'max_temp': stmt.excluded.max_temp,
                'min_temp': stmt.excluded.min_temp,
                'precipitation': stmt.excluded.precipitation
            }
        )
        session.execute(stmt)
        session.commit()


def ingest_weather_data(data_dir="wx_data"):
    engine = get_engine(DB_URL)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    start = datetime.now()
    logger.info("Ingestion started")

    files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    total_attempted = 0
    total_upserted = 0

    for idx, file in enumerate(files, 1):
        station_id = file.replace('.txt', '')
        path = os.path.join(data_dir, file)
        df = pd.read_csv(
            path, sep='\t', header=None,
            names=['date', 'max', 'min', 'precip'], dtype=str
        )

        records = []
        for _, r in df.iterrows():
            d, max_c, min_c, precip_cm = _normalize_row(r)
            records.append(dict(
                station_id=station_id,
                record_date=d,
                max_temp=max_c,
                min_temp=min_c,
                precipitation=precip_cm
            ))

        total_attempted += len(records)
        batch_upsert(session, WeatherData.__table__, records)
        total_upserted += len(records)

        if idx % 10 == 0:
            logger.info(f"Processed {idx}/{len(files)} files")

    session.close()
    end = datetime.now()
    logger.info("Ingestion completed")
    logger.info(f"Duration: {end - start}")
    logger.info(f"Files processed: {len(files)}")
    logger.info(f"Records attempted: {total_attempted}")
    logger.info(f"Records upserted: {total_upserted}")


if __name__ == "__main__":
    create_tables()
    ingest_weather_data()
