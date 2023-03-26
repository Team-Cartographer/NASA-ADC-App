from PIL import Image, ImageDraw
import heapq
from numpy import sqrt
from utils import show_warning, load_json, subdivide_path, get_azi_elev, \
    latitude_from_rect, longitude_from_rect, height_from_rect, slope_from_rect
from ui import get_pathfinding_endpoints
import FileManager as fm
from tqdm import tqdm


class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y

        self.parent = parent

        self.height = grid[y][x][2]
        self.slope = grid[y][x][3]

        self.g = 0
        self.h = 0
        self.f = 0

        if parent is not None:
            self.g = parent.new_g(self)
            self.h = self.heuristic(goal_node)
            self.f = self.g + self.h

    def __lt__(self, other):
        return self.f < other.f

    def heuristic(self, other):
        return self.dist_btw(other)

    def dist_btw(self, other):
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.h - other.h) ** 2)

    def new_g(self, other) -> float:
        # constant values:
        k_dist = 1
        k_slope = 0.25

        slope_penalty = 0  # we could perhaps allow the user to change how much they want to penalize slopes #
        if other.slope >= 20:
            slope_penalty = 25
        elif other.slope >= 8:
            slope_penalty = 5  # see above to do

        dist = self.dist_btw(other)
        slope = abs(self.slope - other.slope)

        eqn = k_dist * dist + k_slope * slope + slope_penalty
        return eqn

def is_valid_checkpoint(point):
    x, y = point[0], point[1]
    azi, elev_earth = get_azi_elev(x, y)

    # if not get_elev_horiz(azi) < elev_earth:
    #     return False

    return True


def astar():
    nodes = []

    heapq.heappush(nodes, start_node)
    visited = set()

    with tqdm(total=None, desc='A* algorithm', unit=" Nodes") as pbar:
        while nodes:
            current = heapq.heappop(nodes)

            if (current.x, current.y) in visited:
                continue
            visited.add((current.x, current.y))

            if current.x == goal_node.x and current.y == goal_node.y and current.height == goal_node.height:
                path = []
                while current.parent:
                    path.append((current.x, current.y, current.height))
                    current = current.parent
                path.append((start_node.x, start_node.y, start_node.height))
                path.reverse()
                return path

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                x2 = current.x + dx
                y2 = current.y + dy

                if 0 <= x2 < len(grid) and 0 <= y2 < len(grid[0]):
                    new_node = Node(x2, y2, current)
                    heapq.heappush(nodes, new_node)

            pbar.update()
    return None


def update_image(image_path: str, mvmt_path: list, comm_path: list):
    path = image_path
    img = Image.open(path)


    for i in tqdm(range(len(mvmt_path)), desc="Updating image"):
        color = (255, 0, 0)
        x = mvmt_path[i][0]
        y = mvmt_path[i][1]
        img.putpixel((x, y), color)

    if comm_path is not None:
        for i in range(len(comm_path)):
            draw = ImageDraw.Draw(img)
            color = (0, 255, 0)
            radius = 3
            draw.ellipse((comm_path[i][0] - radius, comm_path[i][1] - radius,
                          comm_path[i][0] + radius, comm_path[i][1] + radius), fill=color)

    img.save(fm.ASTAR_PATH)


def line_to_earth(x, y):
    # Currently Hardcoded, Fix once we get it working with Regional Site.
    m = (y-1250)/(x-638)
    b = -m*x + y
    return int(m), int(b)


def run_astar():
    (start_x, start_y), (goal_x, goal_y), checkpoints = \
        get_pathfinding_endpoints(fm.get_size_constant(), fm.images_path)

    global grid
    grid = load_json(fm.ASTAR_JSONPATH)

    global start_node, goal_node
    start_node = Node(start_x, start_y)
    goal_node = Node(goal_x, goal_y)

    final_path = astar()
    sub_10_path = None

    if checkpoints:
        sub_10_path = subdivide_path(final_path)
        sub_10_path.insert(0, (start_x, start_y))

    if final_path is not None:
        update_image(fm.TEXTURE_PATH, final_path, sub_10_path)
    else:
        show_warning("A* Pathfinding Error", "No Valid Path found between points.")

    if checkpoints:
        print("Created Path with Communication Checkpoints")
    else:
        print("Created Path")


if __name__ == "__main__":
    run_astar()