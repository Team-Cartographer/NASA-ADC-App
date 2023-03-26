import numpy as np
from utils import timeit
import FileManager as fm
from Constants import LUNAR_RADIUS, EARTH_X, EARTH_Y, EARTH_Z
import time

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

print(time.time()- startt_time)

@timeit
def process_data():
    start_time = time.time()
    # Convert latitudes and longitudes to radians
    latitude_radians = np.radians(latitude_list)
    longitude_radians = np.radians(longitude_list)

    # Calculate the radius
    radius = LUNAR_RADIUS_METERS + height_list

    # Calculate x, y, and z coordinates
    x = radius * np.cos(latitude_radians) * np.cos(longitude_radians)
    y = radius * np.cos(latitude_radians) * np.sin(longitude_radians)
    z = radius * np.sin(latitude_radians)

    # Calculate elevation and azimuth
    dx, dy, dz = EARTH_X_METERS - x, EARTH_Y_METERS - y, EARTH_Z_METERS - z
    r = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    rz = dx * np.cos(latitude_radians) * np.cos(longitude_radians) + dy * np.cos(latitude_radians) * np.sin(longitude_radians) + dz * np.sin(latitude_radians)
    elevation = np.degrees(np.arcsin(rz / r))

    c1 = np.sin(EARTH_LONG - longitude_radians) * np.cos(EARTH_LAT)
    c2 = (np.cos(latitude_radians) * np.sin(EARTH_LAT)) - (np.sin(latitude_radians) * np.cos(EARTH_LAT) * np.cos(EARTH_LONG - longitude_radians))
    azimuth = np.degrees(np.arctan2(c1, c2))

    # Create a_star_data_array
    a_star_data_array = np.column_stack((x.flatten(), y.flatten(), z.flatten(), slope_list.flatten(), azimuth.flatten(), elevation.flatten(), np.degrees(latitude_list).flatten(), np.degrees(longitude_list).flatten(), height_list.flatten()))
    print(time.time() - start_time)
    print(type(a_star_data_array))
    print(a_star_data_array[0])
    print(a_star_data_array[0][0])
    # Save a_star_data_array to CSV file
    # np.savetxt('AStarRawData.csv', a_star_data_array, delimiter=',', header='x,y,z,slope,azimuth,elevation,latitude,longitude,height', comments='')



    # adj_array: list = []
    # for i in tqdm(range(len(a_star_data_array)), desc="Creating AStar Data Array"):
    #     # x[0], y[1], z(height)[2], slope[3], azi[4], elev[5], lat[6], long[7], height[8]
    #     tmp: list = [int(a_star_data_array[i][0]), int(a_star_data_array[i][1]),
    #                  int(a_star_data_array[i][2]),
    #                  a_star_data_array[i][3], a_star_data_array[i][4], a_star_data_array[i][5], a_star_data_array[i][6],
    #                  a_star_data_array[i][7], a_star_data_array[i][8]]
    #     adj_array.append(tmp)
    #
    # sorted_array = sorted(adj_array, key=lambda arr: arr[1])
    #
    # array_to_be_written: list = [[] for _ in range(SIZE)]
    #
    # for i in range(len(sorted_array)):
    #     array_to_be_written[i // SIZE].append(sorted_array[i])
    #
    # for i in range(len(array_to_be_written)):
    #     array_to_be_written[i]: list = sorted(array_to_be_written[i], key=lambda arr: arr[0])
    #
    # for i in range(len(array_to_be_written)):
    #     for j in range(len(array_to_be_written[0])):
    #         array_to_be_written[j][i][0] = i
    #         array_to_be_written[j][i][1] = j
    #
    # push_to_json(fm.ASTAR_JSONPATH, array_to_be_written)


if __name__ == "__main__":
    process_data()
