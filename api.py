import os, math
from flask import Flask, request, jsonify
from flasgger import Swagger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, extract

from schema import WeatherData, WeatherStats, get_engine

DB_URL = os.getenv("DB_URL", "sqlite:///weather.db")
engine = get_engine(DB_URL)
Session = sessionmaker(bind=engine, future=True)

app = Flask(__name__)
app.config["SWAGGER"] = {"title": "Weather API", "uiversion": 3}
swagger = Swagger(app)

def paginate(query, page:int, size:int):
    total = query.count()
    pages = math.ceil(total/size) if size else 1
    items = query.offset((page-1)*size).limit(size).all() if size else query.all()
    return total, pages, items

@app.get("/api/weather")
def api_weather():
    """Get raw weather observations
    ---
    parameters:
      - name: station_id
        in: query
        required: false
        schema:
          type: string
      - name: date
        in: query
        required: false
        schema:
          type: string
          example: 1985-01-01
      - name: page
        in: query
        schema:
          type: integer
          default: 1
      - name: size
        in: query
        schema:
          type: integer
          default: 50
    responses:
      200:
        description: Paginated weather records
    """
    station_id = request.args.get("station_id")
    date = request.args.get("date")  # YYYY-MM-DD
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 50))

    session = Session()
    q = session.query(WeatherData)
    if station_id:
        q = q.filter(WeatherData.station_id == station_id)
    if date:
        q = q.filter(WeatherData.record_date == date)

    q = q.order_by(WeatherData.record_date.asc())
    total, pages, records = paginate(q, page, size)
    data = [{
        "station_id": r.station_id,
        "record_date": r.record_date.isoformat(),
        "max_temp": r.max_temp,
        "min_temp": r.min_temp,
        "precipitation": r.precipitation
    } for r in records]
    session.close()
    return jsonify({"total": total, "pages": pages, "page": page, "data": data})

@app.get("/api/weather/stats")
def api_weather_stats():
    """Get yearly statistics per station
    ---
    parameters:
      - name: station_id
        in: query
        required: false
        schema:
          type: string
      - name: year
        in: query
        required: false
        schema:
          type: integer
      - name: page
        in: query
        schema:
          type: integer
          default: 1
      - name: size
        in: query
        schema:
          type: integer
          default: 50
    responses:
      200:
        description: Paginated yearly weather statistics
    """
    station_id = request.args.get("station_id")
    year = request.args.get("year", type=int)
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 50))

    session = Session()
    q = session.query(WeatherStats)
    if station_id:
        q = q.filter(WeatherStats.station_id == station_id)
    if year is not None:
        q = q.filter(WeatherStats.year == year)

    q = q.order_by(WeatherStats.station_id.asc(), WeatherStats.year.asc())
    total, pages, records = paginate(q, page, size)
    data = [{
        "station_id": r.station_id,
        "year": r.year,
        "avg_max_temp": r.avg_max_temp,
        "avg_min_temp": r.avg_min_temp,
        "total_precipitation": r.total_precipitation
    } for r in records]
    session.close()
    return jsonify({"total": total, "pages": pages, "page": page, "data": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
