from math import radians, cos, sin
from Constants import LUNAR_RADIUS, EARTH_X, EARTH_Y, EARTH_Z

LUNAR_RADIUS_METERS = (LUNAR_RADIUS * 1000)

class Node:
    def __init__(self, latitude: float, longitude: float, height: float, slope: float):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.height: float = height
        self.slope: float = slope

        self.radius: float = LUNAR_RADIUS_METERS + height

        self.latitude_radians: float = radians(latitude)
        self.longitude_radians: float = radians(longitude)

        self.x = calculate_x_coord(self.longitude_radians, self.longitude_radians, self.radius)
        self.y = calculate_y_coord(self.longitude_radians, self.longitude_radians, self.radius)
        self.z = calculate_z_coord(self.longitude_radians, self.radius)


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


def calculate_y_coord(lat: float, long: float, radius: float) -> float:
    """
    Calculate the y-coordinate of a point on a sphere given its latitude, longitude, and radius.

    Note that latitude and longitude should be in radians, and radius should be in meters.

    Args:
        lat (float): Latitude of the point in radians.
        long (float): Longitude of the point in radians.
        radius (float): Radius of the sphere in meters.

    Returns:
        float: The y-coordinate of the point in meters.
    """

    return radius * cos(lat) * sin(long)


def calculate_z_coord(lat: float, rad: float) -> float:
    """
    Calculate the z-coordinate of a point on a sphere given its latitude and radius.

    Note that latitude should be in radians, and radius should be in meters.

    Args:
        lat (float): Latitude of the point in radians.
        rad (float): Radius of the sphere in meters.

    Returns:
        float: The z-coordinate of the point in meters.
    """

    return rad * sin(lat)
