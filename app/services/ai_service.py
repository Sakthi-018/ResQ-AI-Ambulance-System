from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.orm import Session

from app.models.ambulance import Ambulance


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two GPS coordinates.
    Returns distance in kilometers.
    """

    R = 6371  # Earth's radius in KM

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c