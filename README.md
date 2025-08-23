
This repository contains a solution for the **Weather Data Engineering Coding Challenge**, implementing **data ingestion, processing, and a REST API** using **Python, SQLAlchemy, and Flask**. Swagger is included for API documentation.

## Features
- **1. Data modeling**:
  - ORM models using SQLAlchemy representing weather records and yearly statistics
  - Unique constraints to ensure idempotent ingestion
- **2. Idempotent ingestion** of weather data from `wx_data/*.txt` (one file per station).
    - Uses SQLite upsert (ON CONFLICT DO UPDATE) to avoid duplicate records while updating existing entries when necessary
- **3. Data cleaning & conversions**:
  - `-9999` → `NULL` (ignored in statistics).
  - Maximum and minimum temperatures converted from **tenths of °C → °C**.
  - Precipitation converted from **tenths of mm → cm**.
- **4. Yearly aggregated statistics per station**:
  - Average maximum temperature
  - Average minimum temperature
  - Total accumulated precipitation
- **5. REST API** with pagination and filters:
  - `/api/weather` – returns raw weather records
  - `/api/weather/stats` – returns yearly statistics per station
  - Supports filtering by `station_id`, `date` (for `/api/weather`), and `year` (for `/api/weather/stats`)
- **Swagger/OpenAPI documentation** available at `/apidocs`.
- **Unit tests** implemented with `pytest` to validate ingestion, stats, and API endpoints.

## Project Structure
```
schema.py       # SQLAlchemy ORM models & database engine helpers
ingest.py       # Create tables + load raw weather files into DB
stats.py        # Compute and store yearly statistics
api.py          # Flask REST API + Swagger configuration
tests/          # Unit tests for ingestion, stats computation, and API
wx_data/        # Place the provided weather data files here
requirements.txt
README.md
```

## Quickstart

1. **Create & activate virtual environment**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# or
source .venv/bin/activate      # macOS/Linux
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create database tables & ingest raw data**
```bash
python ingest.py
```

4. **Compute yearly statistics**
```bash
python stats.py
```

5. **Run the API**
```bash
python api.py
```
- Access Swagger UI: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)

## API Endpoints

### `GET /api/weather`
- Returns raw weather records.
- **Query Parameters**:
  - `station_id` (optional) – filter by station
  - `date` (optional, YYYY-MM-DD) – filter by specific date
  - `page` (optional, default=1) – pagination
  - `size` (optional, default=50) – page size

### `GET /api/weather/stats`
- Returns yearly statistics per station.
- **Query Parameters**:
  - `station_id` (optional) – filter by station
  - `year` (optional) – filter by year
  - `page` (optional, default=1) – pagination
  - `size` (optional, default=50) – page size

## Notes
- **Database**: SQLite (`weather.db` by default). Override with `DB_URL` environment variable.
- **Idempotency**: Ingestion avoids duplicates using a **unique constraint** on `(station_id, record_date)` and upsert (ON CONFLICT DO UPDATE).
- **Stats recomputation**: Each run overwrites yearly stats to ensure consistency.
- **Error handling & logs**: Logs include start/end times and number of records ingested.
- **Testing**: Run `pytest` in the project root to verify ingestion, stats, and API functionality.
