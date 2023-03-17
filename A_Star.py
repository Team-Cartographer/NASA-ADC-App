from PIL import Image
import heapq
from numpy import sqrt
import csv
from ast import literal_eval
from utils import show_warning
from UserInterface import get_pathfinding_endpoints
import FileManager as fm


class Node:
    def __init__(self, x, y, height, f, g, h, parent=None, slope=None):
        self.x = x
        self.y = y
        self.height = height
        self.f = f
        self.g = g
        self.h = h
        self.parent = parent
        self.slope = slope

    def __lt__(self, other):
        return self.f < other.f


def get_height_and_slope(x, y, grid):
    temp = (grid[y][x])
    temp = literal_eval(temp)
    try:
        if temp == 0:

            print(temp)
            print(x, y)
            print(grid[x])
    except TypeError:
        pass

    return float(temp[2]), float(temp[3])


def distBtw(x1, y1, h1, x2, y2, h2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (h1 - h2) ** 2)


def heuristic(x1, y1, x2, y2, h1, h2):
    heur_rtn = distBtw(x1, y1, h1, x2, y2, h2)
    return heur_rtn


def new_g(cx, cy, ch, cs, nx, ny, nh, ns) -> float:  # c is current node, n is new node
    # constant values:
    k_dist = 1
    k_slope = 0.25

    slope_penalty = 0  # we could perhaps allow the user to change how much they want to penalize slopes
    if ns >= 20:
        slope_penalty = 25  # TODO not have the slope penalty be random numbers. We need to curate these numbers more
    elif ns >= 8:
        slope_penalty = 5  # see above to do

    dist = distBtw(float(cx), float(cy), float(ch), float(nx), float(ny), float(nh))
    slope = abs(cs - ns)

    eqn = k_dist * dist + k_slope * slope + slope_penalty
    return eqn


def astar(grid, start, goal):
    nodes = []
    h, first_slope = get_height_and_slope(start[0], start[1], grid)
    heapq.heappush(nodes, Node(start[0], start[1], start[2], 0, 0, 0, None, first_slope))
    visited = set()

    while nodes:
        current = heapq.heappop(nodes)

        if (current.x, current.y) in visited:
            continue
        visited.add((current.x, current.y))

        if current.x == goal[0] and current.y == goal[1] and current.height == goal[2]:
            path = []
            while current.parent:
                path.append((current.x, current.y, current.height))
                current = current.parent
            path.append((start[0], start[1], start[2]))
            path.reverse()
            return path

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x2 = current.x + dx
            y2 = current.y + dy
            if x2 >= 0 and x2 < len(grid) and y2 >= 0 and y2 < len(grid[0]):
                h2, slope = get_height_and_slope(x2, y2, grid)

                g = current.g + new_g(current.x, current.y, current.height, current.slope, x2, y2, h2, slope)
                h = heuristic(x2, y2, goal[0], goal[1], h2, goal[2])
                f = g + h
                heapq.heappush(nodes, Node(x2, y2, h2, f, g, h, current, slope))

        print(f"\r{(len(visited))/(1277 ** 2)} % complete. Visited {len(visited)} nodes", end="")
    return None


def add_pixel(img, x, y, color):
    img.putpixel((x, y), color)
    return img


def update_image(image_path: str, mvmt_path: list):
    path = image_path
    img = Image.open(path)
    color = (0, 0, 128)
    for i in range(len(mvmt_path)):
        print(f"\rUpdating image. {round(i/len(mvmt_path), 8)}% complete", end="")
        x = mvmt_path[i][0]
        y = mvmt_path[i][1]
        img = add_pixel(img, x, y, color)
    img.save(fm.images_path + "/AStar_Path.png")


if __name__ == "__main__":
    # Test Case

    csv_path = fm.data_path + "/AStarRawData.csv"
    csv_path = csv_path.replace("\\", "/")
    with open(csv_path, mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        full_list = list(csv_reader)

    grid = full_list

    (start_x, start_y), (goal_x, goal_y) = get_pathfinding_endpoints()

    final_path = astar(grid,
                       (start_x, start_y, get_height_and_slope(start_x, start_y, grid)[0], get_height_and_slope(start_x, start_y, grid)[1]),
                       (goal_x, goal_y, get_height_and_slope(goal_x, goal_y, grid)[0], get_height_and_slope(goal_x, goal_y, grid)[1]))
    #print("\nFinal Path: ", final_path)

    try:
        update_image(fm.images_path + '/AStar_Texture.png', final_path)
        print("\rPath Image: ('AStar_Path.png') Created.")
    except TypeError:
        show_warning("A* Pathfinding Error", "No Valid Path found between points.")
        pass

