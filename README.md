
This project is a solution for the Weather Data Engineering Coding Challenge. It includes data ingestion, processing, and a REST API built with Python, SQLAlchemy, and Flask. Swagger is used to provide API documentation.

1. **Data modeling**
  - Designed SQLAlchemy ORM models for weather records and yearly statistics (Tables: weather_data, weather_stats)
  - Unique constraints to support idempotent ingestion


2. **Ingestion and Data cleaning**
  - Loads data from wx_data/*.txt into SQLite database
  - Uses SQLite upsert (ON CONFLICT DO UPDATE) to prevent duplicate records and update existing ones if needed
  - Replaces missing values with NULL
  - Converts temperatures from tenths of °C to °C
  - Converts precipitation from tenths of mm to cm


3. **Data Analysis and API**
  - Calculates Total precipitation, Average maximum and minimum temperature per year for each station
  - /api/weather – raw weather records
  - /api/weather/stats – yearly statistics per station
  - Supports filters for station ID, date/year, and includes pagination
  - Swagger/OpenAPI documentation available at /apidocs

4. Unit tests with pytest to validate ingestion, stats, and API endpoints

**Project Structure**
```
schema.py       - SQLAlchemy ORM models & database engine helpers
ingest.py       - Create tables + load raw weather files into DB
stats.py        - Compute and store yearly statistics
api.py          - Flask REST API + Swagger configuration
tests/          - Unit tests for ingestion, stats computation, and API
wx_data/        - Place the provided weather data files here
requirements.txt
README.md
```

**Usage**

1. Create & activate virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# or
source .venv/bin/activate      # macOS/Linux
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Create database tables & ingest raw data
```bash
python ingest.py
```
4. Compute yearly statistics
```bash
python stats.py
```
5. Run the API
```bash
python api.py
```
- Access Swagger UI: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)
  
**API Endpoints**

- `GET /api/weather`
  - Returns raw weather records.
  - Query Parameters: station_id, date, page, size

- `GET /api/weather/stats`
  - Returns yearly statistics per station.
  - Query Parameters: station_id, date, page, size



**Notes**
- **Database**: SQLite (`weather.db` by default). Override with `DB_URL` environment variable.
- **Idempotency**: Ingestion avoids duplicates using a **unique constraint** on `(station_id, record_date)` and upsert (ON CONFLICT DO UPDATE).
- **Stats recomputation**: Each run overwrites yearly stats to ensure consistency.
- **Error handling & logs**: Logs include start/end times and number of records ingested.
- **Testing**: Run `pytest` in the project root to verify ingestion, stats, and API functionality.

**Data Source**
- Weather data (wx_data/*.txt) and the coding challenge can be found at the below Github repository:
  https://github.com/corteva/code-challenge-template
