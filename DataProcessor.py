import numpy as np
from utils import timeit
import FileManager as fm
from Constants import LUNAR_RADIUS, EARTH_X, EARTH_Y, EARTH_Z
import time
from tqdm import tqdm
from utils import push_to_json, load_json

data = load_json(fm.INFO_JSONPATH)

LUNAR_RADIUS_METERS = (LUNAR_RADIUS * 1000)
EARTH_X_METERS = (EARTH_Y * 1000)
EARTH_Y_METERS = (EARTH_X * 1000)
EARTH_Z_METERS = (EARTH_Z * 1000)

R = np.sqrt(EARTH_X_METERS ** 2 + EARTH_Y_METERS ** 2 + EARTH_Z_METERS ** 2)

EARTH_LAT = np.arcsin(EARTH_Z_METERS / R)
EARTH_LONG = np.arctan2(EARTH_Y_METERS, EARTH_X_METERS)

# Get Constants
SIZE: int = fm.get_size_constant()

startt_time = time.time()


# Creates Lists of each Data Type from the Paths Given.
latitude_list = np.loadtxt(fm.get_latitude_file_path(), delimiter=',', dtype=float)
longitude_list = np.loadtxt(fm.get_longitude_file_path(), delimiter=',', dtype=float)
height_list = np.loadtxt(fm.get_height_file_path(), delimiter=',', dtype=float)
slope_list = np.loadtxt(fm.get_slope_file_path(), delimiter=',', dtype=float)

print(time.time() - startt_time)

@timeit
def process_data():
    start_time = time.time()

    latitude_radians = np.radians(latitude_list)
    longitude_radians = np.radians(longitude_list)

    radius = LUNAR_RADIUS_METERS + height_list

    x = radius * np.cos(latitude_radians) * np.cos(longitude_radians)
    y = radius * np.cos(latitude_radians) * np.sin(longitude_radians)
    z = radius * np.sin(latitude_radians)

    dx, dy, dz = EARTH_X_METERS - x, EARTH_Y_METERS - y, EARTH_Z_METERS - z
    r = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    rz = dx * np.cos(latitude_radians) * np.cos(longitude_radians) + dy * np.cos(latitude_radians) * np.sin(longitude_radians) + dz * np.sin(latitude_radians)
    elevation = np.degrees(np.arcsin(rz / r))

    c1 = np.sin(EARTH_LONG - longitude_radians) * np.cos(EARTH_LAT)
    c2 = (np.cos(latitude_radians) * np.sin(EARTH_LAT)) - (np.sin(latitude_radians) * np.cos(EARTH_LAT) * np.cos(EARTH_LONG - longitude_radians))
    azimuth = np.degrees(np.arctan2(c1, c2))

    a_star_data_array = np.column_stack((x.flatten(), y.flatten(), z.flatten(), slope_list.flatten(), azimuth.flatten(), elevation.flatten(), latitude_list.flatten(), longitude_list.flatten(), height_list.flatten()))
    print(time.time() - start_time)

    min_x: float = np.min(a_star_data_array[:, 0])
    min_y: float = np.min(a_star_data_array[:, 1])
    min_z: float = np.min(a_star_data_array[:, 2])
    max_height: float = np.max(a_star_data_array[:, 8])

    # TODO: Add max x, max y, and  max z to data
    data["MAX_HEIGHT"] = max_height

    a_star_data_array[:, 0] += abs(min_x)
    a_star_data_array[:, 1] += abs(min_y)
    a_star_data_array[:, 2] += abs(min_z)

    a_star_data_array = a_star_data_array[a_star_data_array[:, 1].argsort()]

    a_star_data_array = a_star_data_array.tolist()

    array_to_be_written: list = [[] for _ in range(SIZE)]

    for i in range(len(a_star_data_array)):
        array_to_be_written[i // SIZE].append(a_star_data_array[i])

    for i in range(len(array_to_be_written)):
        array_to_be_written[i]: list = sorted(array_to_be_written[i], key=lambda arr: arr[0])

    push_to_json(fm.ASTAR_JSONPATH, array_to_be_written)
    #push_to_json(fm.INFO_JSONPATH, data)


if __name__ == "__main__":
    process_data()
