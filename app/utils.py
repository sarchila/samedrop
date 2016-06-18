import hashlib
from app import app

TO_MGDL_CONVERSION = {
    'mg_dl': 1,
    'mmol_l': 18
}


def create_hash(identifier):
    return hashlib.sha256((identifier + app.config['SALT']).encode()).hexdigest()


def to_mgdl(reading, units):
    return int(round(float(reading)*TO_MGDL_CONVERSION[units]))
