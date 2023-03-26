from math import radians, cos, sin, sqrt, asin, atan2, degrees
from Constants import LUNAR_RADIUS, EARTH_X, EARTH_Y, EARTH_Z
import numpy as np

LUNAR_RADIUS_METERS = (LUNAR_RADIUS * 1000)
EARTH_X_METERS = (EARTH_Y * 1000)
EARTH_Y_METERS = (EARTH_X * 1000)
EARTH_Z_METERS = (EARTH_Z * 1000)

R = sqrt(EARTH_X_METERS ** 2 + EARTH_Y_METERS ** 2 + EARTH_Z_METERS ** 2)

EARTH_LAT = asin(EARTH_Z_METERS / R)
EARTH_LONG = atan2(EARTH_Y_METERS, EARTH_X_METERS)


class Node:
    def __init__(self, latitude: float, longitude: float, height: float, slope: float):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.height: float = height
        self.slope: float = slope

        self.radius: float = LUNAR_RADIUS_METERS + height

        self.latitude_radians: float = radians(latitude)
        self.longitude_radians: float = radians(longitude)

        self.x: float = calculate_x_coord(self.latitude_radians, self.longitude_radians, self.radius)
        self.y: float = calculate_y_coord(self.latitude_radians, self.longitude_radians, self.radius)
        self.z: float = calculate_z_coord(self.latitude_radians, self.radius)

        self.elevation: float = calculate_elevation(self.latitude_radians, self.longitude_radians, self.x, self.y, self.z)
        self.azimuth: float = calculate_azimuth(self.latitude_radians, self.longitude_radians)


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


def calculate_azimuth(latitude, longitude):
    c1 = sin(EARTH_LONG - longitude) * cos(EARTH_LAT)
    c2 = (cos(latitude) * sin(EARTH_LAT)) - (sin(latitude) * cos(EARTH_LAT) * cos(EARTH_LONG - longitude))

    return degrees(atan2(c1, c2))


def calculate_elevation(latitude, longitude, moon_x, moon_y, moon_z):
    dx = EARTH_X_METERS - moon_x
    dy = EARTH_Y_METERS - moon_y
    dz = EARTH_Z_METERS - moon_z

    r = sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    rz = dx * cos(latitude) * cos(longitude) + dy * cos(latitude) * sin(longitude) + dz * sin(latitude)

    return degrees(asin(rz / r))


# T1:
# 8.180 - 7 - 163/it

# T2:
#
