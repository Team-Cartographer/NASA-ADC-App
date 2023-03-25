from utils import file2list, push_to_json, timeit
import FileManager as fm
from tqdm import tqdm
from Node import Node
import cProfile

# Get Constants
SIZE: int = fm.get_size_constant()

# Creates Lists of each Data Type from the Paths Given.
latitude_list: list = file2list(fm.get_latitude_file_path())
longitude_list: list = file2list(fm.get_longitude_file_path())
height_list: list = file2list(fm.get_height_file_path())
slope_list: list = file2list(fm.get_slope_file_path())


@timeit
def process_data():
    """
    Processes the input data lists containing latitude, longitude, height, and slope values,
    and generates a sorted 3D array of x, y, and z coordinates along with azimuth and elevation values.
    The processed data is written to a CSV file named 'AStarRawData.csv'.
    """

    rows: int = len(longitude_list)
    cols: int = len(longitude_list[0])

    a_star_data_array: list = []
    nodes: list[Node] = []

    for row in tqdm(range(rows), desc="Processing Polar to Rectangular Data"):
        for col in range(cols):
            latitude: float = float(latitude_list[row][col])
            longitude: float = float(longitude_list[row][col])
            height: float = float(height_list[row][col])
            slope: float = float(slope_list[row][col])

            node = Node(latitude, longitude, height, slope)
            # nodes.append(node)

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


# if __name__ == "__main__":
#     process_data()


cProfile.run('process_data()')