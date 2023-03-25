import cProfile
from math import cos


def calculate_x_coord(lat: float, long: float, radius: float) -> float:
    """
    Calculate the x-coordinate of a point on a sphere given its latitude, longitude, and radius.

    Note that latitude and longitude should be in radians, and radius should be in meters.

    Args:
        lat (float): Latitude of the point in radians.
        long (float): Longitude of the point in radians.
        radius (float): Radius of the sphere in meters.

    Returns:
        float: The x-coordinate of the point in meters.
    """

    return radius * cos(lat) * cos(long)


def main():
    # Call your function here with some example inputs
    lat = 0.5  # 30 degrees in radians
    long = 1.0  # 60 degrees in radians
    radius = 6371000  # Earth's mean radius in meters
    x_coord = calculate_x_coord(lat, long, radius)


