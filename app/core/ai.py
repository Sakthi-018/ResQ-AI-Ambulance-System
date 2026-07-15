from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM

    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# =====================================================
# Find Nearest Ambulance
# =====================================================
def find_nearest_ambulance(ambulances, user_lat, user_lon):

    nearest = None
    min_distance = float("inf")

    for ambulance in ambulances:

        distance = haversine(
            user_lat,
            user_lon,
            ambulance.latitude,
            ambulance.longitude
        )

        if distance < min_distance:
            min_distance = distance
            nearest = ambulance

    return nearest, min_distance


# =====================================================
# Find Best Hospital
# =====================================================
def find_nearest_hospital(hospitals, user_lat, user_lon):

    best_hospital = None
    best_distance = 0
    best_score = -1

    for hospital in hospitals:

        distance = haversine(
            user_lat,
            user_lon,
            hospital.latitude,
            hospital.longitude
        )

        if distance == 0:
            distance = 0.1

        score = hospital.available_beds / (distance ** 2)

        print(
            f"{hospital.name} | Distance={distance:.2f} km | Beds={hospital.available_beds} | Score={score:.2f}"
        )

        if score > best_score:
            best_score = score
            best_distance = distance
            best_hospital = hospital

    return best_hospital, best_distance

def predict_eta(distance_km):
    """
    Estimate ambulance arrival time.

    Assumption:
    Average ambulance speed = 40 km/h
    """

    average_speed = 40

    eta_hours = distance_km / average_speed

    eta_minutes = round(eta_hours * 60)

    return eta_minutes