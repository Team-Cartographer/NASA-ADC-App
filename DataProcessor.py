"""
This program takes data from four csv files, latitude values, longitude values, height values, slope values. The
program then repackages this data as an array of objects and writes it to a csv file named "RawDataArray.csv". The
program then calculates the rectangular coordinates for each data point using formulas for converting latitude,
longitude, and height to Cartesian coordinates. It then writes this data to a csv file named
"RectangularCoordinateData.csv". Finally, the program sorts and formats the rectangular coordinate data in
preparation for use in an A-star algorithm and writes it to a csv file named "AStarRawData.csv".
"""
from __future__ import annotations

from ast import literal_eval
import csv
from sys import exit
import FileManager as fm
from utils import file2list, get_x_coord, get_y_coord, get_z_coord, get_azimuth, get_elevation
from dotenv import set_key

DISTANCE_BETWEEN_POINTS: int = fm.get_dist_between_points()
SIZE = fm.get_size_constant()
# Creates Lists of each Data Type from the Paths Given.
latitude_list: list = file2list(fm.get_latitude_file_path())
longitude_list: list = file2list(fm.get_longitude_file_path())
height_list: list = file2list(fm.get_height_file_path())
slope_list: list = file2list(fm.get_slope_file_path())


def generate_data_array() -> tuple[int, str] | None:
    if not len(longitude_list) == len(latitude_list) == len(height_list) == len(slope_list):
        fm.show_error("ADC App Data Processing Failure", f'Data List Row Lengths are Inconsistent.')
        return

    if not len(longitude_list[0]) == len(latitude_list[0]) == len(height_list[0]) == len(slope_list[0]):
        fm.show_error("ADC App Data Processing Failure", f'Data List Column Lengths are Inconsistent.')
        return

    rows: int = len(longitude_list)
    cols: int = len(longitude_list[0])
    xy_dim: int = len(longitude_list)

    # Change to {fc.archive_path} for final build.
    data_array_path_: str = fm.data_path + "/RawDataArray.csv"

    with open(data_array_path_, mode="w", newline="") as f:
        csv_writer: csv.writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in range(rows):
            for data_pt in range(cols):
                # dataArray[k][0] = Lat, dA[k][1] = long, dA[k][2] = ht, dA[k][3] = slope
                latitude: float = float(latitude_list[row][data_pt])
                longitude: float = float(longitude_list[row][data_pt])
                height: float = float(height_list[row][data_pt])
                slope: float = float(slope_list[row][data_pt])

                tmp: list = [latitude, longitude, height,slope]
                dataArray.append(tmp)
                csv_writer.writerow(tmp)

    f.close()
    print("Created RawDataArray.csv")

    return xy_dim, data_array_path_


def write_rect_file(data_arr) -> tuple[str, float, float, float]:
    rect_coord_path: str = fm.data_path + "/RectangularCoordinateData.csv"
    xs: list = []
    ys: list = []
    zs: list = []
    length: int = len(data_arr)
    with open(rect_coord_path, mode="w", newline="") as datafile:
        csv_writer: csv.writer = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(length):
            lat: float = data_arr[i][0]
            long: float = data_arr[i][1]
            height: float = data_arr[i][2]
            slope: float = data_arr[i][3]
            height: float = fm.get_lunar_rad() + float(height)  # Technically Radius

            x: float = float(get_x_coord(lat, long, height)) / DISTANCE_BETWEEN_POINTS
            y: float = float(get_y_coord(lat, long, height)) / DISTANCE_BETWEEN_POINTS
            z: float = float(get_z_coord(lat, height)) / DISTANCE_BETWEEN_POINTS
            azi: float = get_azimuth(lat, long)
            elev: float = get_elevation(lat, long, height)
            csv_writer.writerow([x, y, z, slope, azi, elev, lat, long])
            xs.append(x), ys.append(y), zs.append(z)
            tmpDataArray.append([x, y, z, slope, azi, elev, lat, long])
            print(f"\rCreating RectangularCoordinateData.csv. {round(i / length, 4)}% complete", end="")

        datafile.close()
    min_x_: float = abs(min(xs))
    min_y_: float = abs(min(ys))
    min_z_: float = abs(min(zs))
    max_z: str = str(round(abs(min_z_) - abs(max(zs))))
    set_key('.env', 'MAX_Z', max_z)
    set_key('.env', 'MIN_Z', str(min_z_))
    set_key('.env', 'MIN_X', str(min_x_))
    set_key('.env', 'MIN_Y', str(min_y_))

    print("\nCreated RectangularCoordinateData.csv")
    return rect_coord_path, min_x_, min_y_, min_z_

# TODO Could be causing Streaking, take a look at it.
def write_astar_file(min_x_, min_y_, min_z_, temp_array) -> str:
    adj_array: list = []
    for i in range(len(temp_array)):
        # x[0], y[1], z(height)[2], slope[3], azi[4], elev[5], lat[6], long[7]
        tmp: list = [int(temp_array[i][0] + min_x_), int(temp_array[i][1] + min_y_), int(temp_array[i][2] + min_z_),
               temp_array[i][3], temp_array[i][4], temp_array[i][5], temp_array[i][6],
               temp_array[i][7]]
        adj_array.append(tmp)

    sorted_array: list = sorted(adj_array, key=lambda x: x[1])

    array_to_be_written: list = []
    for i in range(SIZE):
        array_to_be_written.append([])

    for i in range(len(sorted_array)):
        array_to_be_written[i // SIZE].append(sorted_array[i])

    for i in range(len(array_to_be_written)):
        array_to_be_written[i]: list = sorted(array_to_be_written[i], key=lambda x: x[0])

    for i in range(len(array_to_be_written)):
        for j in range(len(array_to_be_written[0])):
            array_to_be_written[j][i][0] = i
            array_to_be_written[j][i][1] = j

    # Retrofitted A-Star Data
    astar_path: str = fm.data_path + "/AStarRawData.csv"
    with open(astar_path, mode="w", newline="") as f:
        csv_writer: csv.writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in array_to_be_written:
            csv_writer.writerow(row)
    f.close()
    print("Created AStarRawData.csv")

    return astar_path


def test_astar_file():
    astar_path: str = fm.data_path + "/AStarRawData.csv"
    with open(astar_path, mode="r", newline="") as f:
        astar_data: list = list(csv.reader(f))

    for j in range(len(astar_data)):
        for i in range(len(astar_data[0])):
            if literal_eval(astar_data[j][i])[0] != i:
                if literal_eval(astar_data[j][i])[1] != j:
                    print(astar_data[j][i])
                    print(i, j)
                    exit(2)


if __name__ == "__main__":
    # Latitude is DataArr[0], Longitude is DataArr[1], Height is DataArr[2], Slope is DataArr[3]
    dataArray: list = []
    tmpDataArray: list = []
    x_and_y_dim, data_array_path = generate_data_array()

    rect_file_path, min_x, min_y, min_z, = write_rect_file(dataArray)
    sorted_file_path: str = write_astar_file(min_x, min_y, min_z, tmpDataArray)
    # test_astar_file()
    print("Data Processing Success")
