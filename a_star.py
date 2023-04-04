from PIL import Image, ImageDraw
import heapq
from numpy import sqrt, load
from utils import show_warning, subdivide_path, height_from_rect
from ui import get_pathfinding_endpoints
from typing import List, Tuple, Union


GRID = load("pathfinding/grid.npy")
SIZE = len(GRID)


class Node:
    def __init__(self, x: int, y: int, parent: "Node" = None) -> None:
        self.x = x
        self.y = y

        self.parent = parent

        self.height = GRID[y][x][2]
        self.slope = GRID[y][x][3]

        self.g: float = 0
        self.h: float = 0
        self.f: float = 0

        if parent is not None:
            self.g = parent.new_g(self)
            self.h = self.heuristic(goal_node)
            self.f = self.g + self.h

    def __lt__(self, other: "Node") -> bool:
        return self.f < other.f

    def heuristic(self, other: "Node") -> float:
        return self.dist_btw(other)

    def dist_btw(self, other: "Node") -> float:
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.height - other.height) ** 2)

    def new_g(self, other: "Node") -> float:
        # constant values:
        k_dist: float = 1
        k_slope: float = 0.25

        slope_penalty: float = 0  # we could perhaps allow the user to change how much they want to penalize slopes #
        if other.slope >= 15:
            slope_penalty = 25
        elif other.slope >= 8:
            slope_penalty = 5  # see above to do

        dist: float = self.dist_btw(other)
        slope: float = abs(self.slope - other.slope)

        eqn: float = k_dist * dist + k_slope * slope + slope_penalty
        return eqn


# noinspection PyPep8Naming
def is_valid_checkpoint(point: tuple[int, int]) -> bool:
    x, y = point[0], point[1]
    height = height_from_rect(x, y, GRID)

    ALLOWANCE: int = 275  # Change this to change the stringency of checkpoint validity

    for i in range(y, SIZE):
        if height_from_rect(x, i, GRID) > (height + ALLOWANCE):
            return False

    return True


# noinspection PyGlobalUndefined
# noinspection PyPep8Naming
def generate_comm_path(comm_path: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int]]]:
    for index, point in enumerate(comm_path):

        print(f"\rgenerating communication checkpoints: {round(index / len(comm_path) * 100, 2)}% complete", end="")

        x, y = point[0], point[1]
        # If a point is already valid, then just leave it.
        if is_valid_checkpoint(point):
            continue

        # Define the bounds of the square, using max/min as point validity fail safes.
        SEARCH_AREA: int = 150
        left_bound: int = max(0, x - SEARCH_AREA)
        right_bound: int = min(SIZE - 1, x + SEARCH_AREA)
        top_bound: int = max(0, y - SEARCH_AREA)
        bottom_bound: int = min(SIZE - 1, y + SEARCH_AREA)

        # Loop through each square per each checkpoint. If it's valid, then replace it.
        for i in range(left_bound, right_bound + 1):
            for j in range(top_bound, bottom_bound + 1):
                test_point = (i, j)
                if is_valid_checkpoint(test_point):
                    comm_path[index] = test_point
                # else:
                #    show_warning("Pathfinding Error", "No valid path with checkpoints was found.")
                #    quit(1)

    print("\n")

    # Now we generate a new path.
    final_path: List[Tuple[int, int, int]] = []
    for i in range(len(comm_path) - 1):
        (start_x, start_y), (goal_x, goal_y) = \
            (comm_path[i][0], comm_path[i][1]), (comm_path[i+1][0], comm_path[i+1][1])
        global start_node
        global goal_node
        start_node = Node(start_x, start_y)
        goal_node = Node(goal_x, goal_y)

        path_btw = astar()
        final_path.extend(path_btw)

    return final_path, comm_path


# noinspection SpellCheckingInspection
def astar() -> Union[List[Tuple[int, int, int]], None]:
    nodes: List[Node] = []

    heapq.heappush(nodes, start_node)
    visited = set()

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

            if 0 <= x2 < len(GRID) and 0 <= y2 < len(GRID[0]):
                new_node = Node(x2, y2, current)
                heapq.heappush(nodes, new_node)

    return None


# noinspection SpellCheckingInspection
def update_image(image_path: str, mvmt_path: List[tuple], comm_path: List[tuple]):
    path: str = image_path
    img: Image.Image = Image.open(path)

    print("updating path image")
    for i in range(len(mvmt_path)):
        color: tuple = (255, 0, 0)
        x: int = mvmt_path[i][0]
        y: int = mvmt_path[i][1]
        img.putpixel((x, y), color)

    if comm_path is not None:
        for i in range(len(comm_path)):
            draw: ImageDraw.ImageDraw = ImageDraw.Draw(img)
            color: tuple = (0, 255, 0)
            radius: int = 3
            draw.ellipse((comm_path[i][0] - radius, comm_path[i][1] - radius,
                          comm_path[i][0] + radius, comm_path[i][1] + radius), fill=color)

    img.save(save.astar_path_image)


# noinspection SpellCheckingInspection
# noinspection PyGlobalUndefined
def run_astar(sv) -> None:
    print("finding a suitable lunar path")
    global save
    save = sv

    global SIZE
    global GRID
    SIZE = save.size
    GRID = load(save.data_file)

    (start_x, start_y), (goal_x, goal_y), checkpoints = get_pathfinding_endpoints(save)

    # For Future Testing
    # (start_x, start_y), (goal_x, goal_y), checkpoints = (306, 1013), (669, 273), True

    global start_node
    global goal_node
    start_node = Node(start_x, start_y)
    goal_node = Node(goal_x, goal_y)

    final_path = astar()
    print("initial path generated")
    sub_10_path = None

    if checkpoints:
        sub_10_path = subdivide_path(final_path)
        sub_10_path.insert(0, (start_x, start_y))
        final_path, sub_10_path = generate_comm_path(sub_10_path)

    if final_path is not None:
        update_image(save.moon_surface_texture_image, final_path, sub_10_path)
    else:
        show_warning("A* Pathfinding Error", "No Valid Path found between points.")

    if checkpoints:
        print("Created Path with Communication Checkpoints")
    else:
        print("Created Path without Communication Checkpoints")


if __name__ == "__main__":
    pass
