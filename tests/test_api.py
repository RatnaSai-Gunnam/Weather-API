import os
import tempfile
from schema import Base, WeatherData, WeatherStats, get_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

# Use Flask app in testing mode
from api import app, Session

def setup_module(module):
    # Create fresh DB
    engine = get_engine("sqlite:///weather.db")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # Seed a couple rows
    s = Session()
    s.add_all([
        WeatherData(station_id='TEST', record_date=date(1985,1,1), max_temp=1.0, min_temp=-1.0, precipitation=0.5),
        WeatherData(station_id='TEST', record_date=date(1985,1,2), max_temp=3.0, min_temp=0.0, precipitation=0.2),
    ])
    s.add(WeatherStats(station_id='TEST', year=1985, avg_max_temp=2.0, avg_min_temp=-0.5, total_precipitation=0.7))
    s.commit()
    s.close()

def test_weather_endpoint():
    client = app.test_client()
    resp = client.get('/api/weather?station_id=TEST&size=10')
    assert resp.status_code == 200
    data = resp.get_json()['data']
    assert len(data) == 2
    assert data[0]['station_id'] == 'TEST'

def test_stats_endpoint():
    client = app.test_client()
    resp = client.get('/api/weather/stats?station_id=TEST')
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['data'][0]['year'] == 1985
