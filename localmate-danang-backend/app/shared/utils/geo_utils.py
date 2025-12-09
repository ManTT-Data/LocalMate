"""Geographic utility functions."""

import math


def haversine_distance(
    point1: tuple[float, float],
    point2: tuple[float, float],
) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Uses the Haversine formula.

    Args:
        point1: (latitude, longitude) of first point
        point2: (latitude, longitude) of second point

    Returns:
        Distance in kilometers
    """
    lat1, lon1 = point1
    lat2, lon2 = point2

    # Earth's radius in kilometers
    R = 6371.0

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def bounding_box(
    lat: float,
    lng: float,
    radius_km: float,
) -> tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point.

    Args:
        lat: Center latitude
        lng: Center longitude
        radius_km: Radius in kilometers

    Returns:
        (min_lat, min_lng, max_lat, max_lng)
    """
    # Approximate degrees per km
    lat_delta = radius_km / 111.0  # 1 degree lat ≈ 111 km
    lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    return (
        lat - lat_delta,
        lng - lng_delta,
        lat + lat_delta,
        lng + lng_delta,
    )
