import sys

import FileManager as fm
from utils import file2list, get_x_coord, get_y_coord, \
    get_z_coord, get_azimuth, get_elevation, timeit, \
    load_json, push_to_json
from tqdm import tqdm
from math import sin, cos, radians, degrees, atan2, asin, sqrt

# Get Constants

SIZE: int = fm.get_size_constant()
LUNAR_RAD: float = fm.get_lunar_rad()

# Legacy Constants
# DISTANCE_BETWEEN_POINTS: int = fm.get_dist_between_points()


# Creates Lists of each Data Type from the Paths Given.
latitude_list: list = file2list(fm.get_latitude_file_path())
longitude_list: list = file2list(fm.get_longitude_file_path())
height_list: list = file2list(fm.get_height_file_path())
slope_list: list = file2list(fm.get_slope_file_path())

data = load_json(fm.INFO_JSONPATH)


earth_x = 361000  # IN KM (p 17)
earth_y = 0  # IN KM (p 17)
earth_z = -42100  # IN KM (p 17)

@timeit
def process_data():
    """
    Processes the input data lists containing latitude, longitude, height, and slope values,
    and generates a sorted 3D array of x, y, and z coordinates along with azimuth and elevation values.
    The processed data is written to a CSV file named 'AStarRawData.csv'.
    """

    rows: int = len(longitude_list)
    cols: int = len(longitude_list[0])

    xs: list = []
    ys: list = []
    zs: list = []
    heights: list = []

    a_star_data_array: list = []

    for row in tqdm(range(rows), desc="Processing Polar to Rectangular Data"):
        for col in range(cols):
            latitude: float = float(latitude_list[row][col])
            longitude: float = float(longitude_list[row][col])
            height: float = float(height_list[row][col])
            slope: float = float(slope_list[row][col])

            radius: float = LUNAR_RAD + float(height)

            latitude = radians(latitude)
            longitude = radians(longitude)

            x = radius * cos(latitude) * cos(longitude)
            y = radius * cos(latitude) * sin(longitude)
            z = radius * sin(latitude)

            dx = (earth_x * 1000) - x
            dy = (earth_y * 1000) - y
            dz = (earth_z * 1000) - z

            r = sqrt(dx ** 2 + dy ** 2 + dz ** 2)
            rz = dx * cos(latitude) * cos(longitude) + dy * cos(latitude) * sin(longitude) + dz * sin(latitude)

            xx = 361000 * 1000
            yy = 0
            zz = -42100 * 1000

            rr = sqrt(xx ** 2 + yy ** 2 + zz ** 2)

            earth_lat = asin(zz / rr)
            earth_long = atan2(yy, xx)

            #  A = moon, B = earth
            p1 = sin(earth_long - longitude) * cos(earth_lat)
            p2 = (cos(latitude) * sin(earth_lat)) - (sin(latitude) * cos(earth_lat) * cos(earth_long - longitude))

            elev = asin(rz / r)
            azi = atan2(p1, p2)

            elev_deg = degrees(elev)
            azi_deg = degrees(azi)

            # azi: float = get_azimuth(latitude, longitude)
            # elev: float = get_elevation(latitude, longitude, x, y, z)

            xs.append(x), ys.append(y), zs.append(z), heights.append(azi_deg)

            a_star_data_array.append([x, y, z, slope, azi_deg, elev_deg, degrees(latitude), degrees(longitude), height])

    min_x_: float = abs(min(xs))
    min_y_: float = abs(min(ys))
    min_z_: float = abs(min(zs))
    min_height_: float = abs(min(heights))
    print(min(heights), max(heights))
    max_z: float = (round(abs(min_z_) - abs(max(zs))))
    max_height_: float = (round(min_height_ + abs(max(heights))))

    # Update .env (Soon to be outdated with .json)
    data["MAX_Z"] = max_z
    data["MIN_Z"] = min_z_
    data["MIN_Y"] = min_y_
    data["MIN_X"] = min_x_
    data["MIN_HEIGHT"] = min_height_
    data["MAX_HEIGHT"] = max_height_

    adj_array: list = []
    for i in tqdm(range(len(a_star_data_array)), desc="Creating AStar Data Array"):
        # x[0], y[1], z(height)[2], slope[3], azi[4], elev[5], lat[6], long[7], height[8]
        tmp: list = [int(a_star_data_array[i][0] + min_x_), int(a_star_data_array[i][1] + min_y_),
                     int(a_star_data_array[i][2] + min_z_),
                     a_star_data_array[i][3], a_star_data_array[i][4], a_star_data_array[i][5], a_star_data_array[i][6],
                     a_star_data_array[i][7], a_star_data_array[i][8]]
        adj_array.append(tmp)

    sorted_array = sorted(adj_array, key=lambda arr: arr[1])

    array_to_be_written: list = [[] for _ in range(SIZE)]

    for i in range(len(sorted_array)):
        array_to_be_written[i // SIZE].append(sorted_array[i])

    for i in range(len(array_to_be_written)):
        array_to_be_written[i]: list = sorted(array_to_be_written[i], key=lambda arr: arr[0])

    for i in range(len(array_to_be_written)):
        for j in range(len(array_to_be_written[0])):
            array_to_be_written[j][i][0] = i
            array_to_be_written[j][i][1] = j

    push_to_json(fm.ASTAR_JSONPATH, array_to_be_written)
    push_to_json(fm.INFO_JSONPATH, data)


if __name__ == "__main__":
    process_data()
