import csv
import FileManager as fm
from utils import file2list, get_x_coord, get_y_coord, get_z_coord, get_azimuth, get_elevation
from dotenv import set_key
from tqdm import tqdm

# Get Constants
DISTANCE_BETWEEN_POINTS: int = fm.get_dist_between_points()
SIZE = fm.get_size_constant()
LUNAR_RAD = fm.get_lunar_rad()

# Creates Lists of each Data Type from the Paths Given.
latitude_list: list = file2list(fm.get_latitude_file_path())
longitude_list: list = file2list(fm.get_longitude_file_path())
height_list: list = file2list(fm.get_height_file_path())
slope_list: list = file2list(fm.get_slope_file_path())


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

    tmpDataArray: list = []

    for row in tqdm(range(rows), desc="Processing Polar to Rectangular Data"):
        for col in range(cols):
            latitude: float = float(latitude_list[row][col])
            longitude: float = float(longitude_list[row][col])
            height: float = float(height_list[row][col])
            slope: float = float(slope_list[row][col])

            radius: float = LUNAR_RAD + float(height)

            x: float = float(get_x_coord(latitude, longitude, radius)) / DISTANCE_BETWEEN_POINTS
            y: float = float(get_y_coord(latitude, longitude, radius)) / DISTANCE_BETWEEN_POINTS
            z: float = float(get_z_coord(latitude, radius)) / DISTANCE_BETWEEN_POINTS

            azi: float = get_azimuth(latitude, longitude)
            elev: float = get_elevation(latitude, longitude, radius)

            xs.append(x), ys.append(y), zs.append(z)

            tmpDataArray.append([x, y, z, slope, azi, elev, latitude, longitude])

    min_x_: float = abs(min(xs))
    min_y_: float = abs(min(ys))
    min_z_: float = abs(min(zs))

    max_z: str = str(round(abs(min_z_) - abs(max(zs))))

    # Update .env (Soon to be outdated with .json)
    set_key('.env', 'MAX_Z', max_z)
    set_key('.env', 'MIN_Z', str(min_z_))
    set_key('.env', 'MIN_X', str(min_x_))
    set_key('.env', 'MIN_Y', str(min_y_))

    adj_array: list = []
    for i in tqdm(range(len(tmpDataArray)), desc="Creating AStar Data Array"):
        # x[0], y[1], z(height)[2], slope[3], azi[4], elev[5], lat[6], long[7]
        tmp: list = [int(tmpDataArray[i][0] + min_x_), int(tmpDataArray[i][1] + min_y_),
                     int(tmpDataArray[i][2] + min_z_),
                     tmpDataArray[i][3], tmpDataArray[i][4], tmpDataArray[i][5], tmpDataArray[i][6],
                     tmpDataArray[i][7]]
        adj_array.append(tmp)

    sorted_array = sorted(adj_array, key=lambda arr: arr[1])

    array_to_be_written: list = [[] for _ in range(SIZE)]

    for i in range(len(sorted_array)):
        array_to_be_written[i // SIZE].append(sorted_array[i])

    for i in range(len(array_to_be_written)):
        array_to_be_written[i]: list = sorted(array_to_be_written[i], key=lambda x: x[0])


    for i in range(len(array_to_be_written)):
        for j in range(len(array_to_be_written[0])):
            array_to_be_written[j][i][0] = i
            array_to_be_written[j][i][1] = j


    astar_path: str = fm.data_path + "/AStarRawData.csv"
    with open(astar_path, mode="w", newline="") as f:
        csv_writer: csv.writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in tqdm(array_to_be_written, desc='Writing to AStarRawData.csv'):
            csv_writer.writerow(row)
    f.close()

if __name__ == "__main__":
    process_data()
    print("Data Processing Success")
