import FileManager as fm
from utils import file2list, get_x_coord, get_y_coord, get_z_coord, get_azimuth, get_elevation
from tqdm import tqdm

# Get Constants
DISTANCE_BETWEEN_POINTS: int = fm.get_dist_between_points()
SIZE: int = fm.get_size_constant()
LUNAR_RAD: float = fm.get_lunar_rad()

# Creates Lists of each Data Type from the Paths Given.
latitude_list: list = file2list(fm.get_latitude_file_path())
longitude_list: list = file2list(fm.get_longitude_file_path())
height_list: list = file2list(fm.get_height_file_path())
slope_list: list = file2list(fm.get_slope_file_path())

data = fm.load_json(fm.JSONPATH)


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

    a_star_data_array: list = []

    for row in tqdm(range(rows), desc="Processing Polar to Rectangular Data"):
        for col in range(cols):
            latitude: float = float(latitude_list[row][col])
            longitude: float = float(longitude_list[row][col])
            height: float = float(height_list[row][col])
            slope: float = float(slope_list[row][col])

            radius: float = LUNAR_RAD + float(height)

            x: float = float(get_x_coord(latitude, longitude, radius))
            y: float = float(get_y_coord(latitude, longitude, radius))
            z: float = float(get_z_coord(latitude, radius))

            azi: float = get_azimuth(latitude, longitude)
            elev: float = get_elevation(latitude, longitude, radius)

            xs.append(x), ys.append(y), zs.append(z)

            a_star_data_array.append([x, y, z, slope, azi, elev, latitude, longitude])

    min_x_: float = abs(min(xs))
    min_y_: float = abs(min(ys))
    min_z_: float = abs(min(zs))

    max_z: float = (round(abs(min_z_) - abs(max(zs))))

    # Update .env (Soon to be outdated with .json)
    data["MAX_Z"] = max_z
    data["MIN_Z"] = min_z_
    data["MIN_Y"] = min_y_
    data["MIN_X"] = min_x_

    adj_array: list = []
    for i in tqdm(range(len(a_star_data_array)), desc="Creating AStar Data Array"):
        # x[0], y[1], z(height)[2], slope[3], azi[4], elev[5], lat[6], long[7]
        tmp: list = [int(a_star_data_array[i][0] + min_x_), int(a_star_data_array[i][1] + min_y_),
                     int(a_star_data_array[i][2] + min_z_),
                     a_star_data_array[i][3], a_star_data_array[i][4], a_star_data_array[i][5], a_star_data_array[i][6],
                     a_star_data_array[i][7]]
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

    fm.push_to_json(fm.data_path + "/AStarRawData.json", array_to_be_written, None)
    fm.push_to_json(fm.JSONPATH, data)


if __name__ == "__main__":
    process_data()
