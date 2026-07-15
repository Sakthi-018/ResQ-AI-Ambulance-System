from sqlalchemy.orm import Session

from app.models.ambulance import Ambulance
from app.ai.distance import calculate_distance


def find_nearest_ambulance(
    user_lat: float,
    user_lon: float,
    db: Session
):
    """
    Find the nearest AVAILABLE ambulance.
    """

    ambulances = (
        db.query(Ambulance)
        .filter(Ambulance.status == "Available")
        .all()
    )

    if not ambulances:
        return None

    nearest = None
    shortest_distance = float("inf")

    for ambulance in ambulances:

        if ambulance.latitude is None or ambulance.longitude is None:
            continue

        distance = calculate_distance(
            user_lat,
            user_lon,
            ambulance.latitude,
            ambulance.longitude
        )

        if distance < shortest_distance:
            shortest_distance = distance
            nearest = ambulance

    return nearest