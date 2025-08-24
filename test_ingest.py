import os
import tempfile
from schema import Base, get_engine, WeatherData
from sqlalchemy.orm import sessionmaker
from ingest import _normalize_row

def test_normalize_row():
    row = { 'date':'19850101', 'max':'-9999', 'min':'22', 'precip':'94' }
    d, max_c, min_c, precip_cm = _normalize_row(row)
    assert str(d) == '1985-01-01'
    assert max_c is None
    assert abs(min_c - 2.2) < 1e-6
    assert abs(precip_cm - 0.94) < 1e-6
