from __future__ import annotations
import csv
import tkinter as tk
from tkinter import messagebox
import os
from numpy import rad2deg, deg2rad
from math import atan2, sin, cos, asin, sqrt
from ast import literal_eval
from PIL import Image # of deez nuts (sorry)
import pygame
from pygame import gfxdraw
from webbrowser import open as open_page

def file2list(path):
    with open(path) as csv_file:
        new_list = list(csv.reader(csv_file, delimiter=','))
        csv_file.close()

    return new_list

try:
    astar_list = file2list(os.getcwd() + '/Data/AStarRawData.csv')
except FileNotFoundError:
    pass

def open_webpage(url : str) -> None:
    open_page(url)

def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


# Since FolderCreator is used across each file, these helper methods allow
# creating an error/info/warning popUp in each file.
def show_error(err_type, msg):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(err_type, msg)


def show_info(title, msg):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, msg)


def show_warning(title, msg):
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(title, msg)

# Display Calculations (Helper Functions for Math)
def get_radius(x: float, y: float) -> float:
    return sqrt((x**2) + (y**2))

def latitude_from_rect(x: float, y: float, radius: float) -> float:
    #lat, _, _ = (radius/(30366 + (1/9))) - 90, x, y
    lat = literal_eval(astar_list[x][y])[6]
    return lat

def longitude_from_rect(x: float, y: float, radius: float) -> float:
    #long, _ = rad2deg(arccos(x/radius)), y
    long = literal_eval(astar_list[x][y])[7]
    return long

def slope_from_rect(x: float, y: float) -> float:
    return literal_eval(astar_list[x][y])[3]

def height_from_rect(x: float, y: float) -> float:
    height = float(os.getenv("MAX_Z")) - literal_eval(astar_list[x][y])[2]
    return height

def get_x_coord(lat, long, rad):  # takes in degrees latitude and longitude
    return float(rad) * cos(deg2rad(float(lat))) * cos(deg2rad(float(long)))

def get_y_coord(lat, long, rad):
    return float(rad) * cos(deg2rad(float(lat))) * sin(deg2rad(float(long)))

def get_z_coord(lat, rad):
    return float(rad) * sin(deg2rad(float(lat)))

# ONLY FOR USE WITH Display.py
def get_azi_elev(x, y):
    data = literal_eval(astar_list[x][y])
    return round(data[4], 5), round(data[5], 5) # azimuth and elevation, respectively


def get_azimuth(moon_lat, moon_long):
    """
    Gets Azimuth based on Latitude and Longitude for DataProcessor

    Keyword arguments:\n
    moon_lat -- latitude of Player pos. in Display.py
    moon_long -- longitude of Player pos. in Display.py
    """

    # True Lunar South Pole
    lunar_south_pole_lat, lunar_south_pole_long = deg2rad(-89.54), deg2rad(0)
    moon_lat_radian = deg2rad(float(moon_lat))
    moon_long_radian = deg2rad(float(moon_long))

    # Azimuth Calculation
    c1 = sin(moon_long_radian - lunar_south_pole_long) * cos(moon_lat_radian)
    c2 = (cos(lunar_south_pole_lat) * sin(moon_lat_radian)) - (sin(lunar_south_pole_lat) * cos(moon_lat_radian) * cos(moon_long_radian - lunar_south_pole_long))
    azi = atan2(c1, c2)

    return rad2deg(azi)


def get_elevation(moon_lat, moon_long, moon_height):
    # Elevation Calculation for DataProcessor.py
    # Earth Cartesian Position with respect to Lunar Fixed Frame at a single time instant
    # [X, Y, Z] = [361000, 0, –42100] km.


    earth_x = 361000
    earth_y = 0
    earth_z = -42100

    moon_lat_rad = deg2rad(float(moon_lat))
    moon_long_rad = deg2rad(float(moon_long))
    moon_radius = 1737.4 * 1000 + float(moon_height)

    moon_x = get_x_coord(moon_lat, moon_long, moon_radius)
    moon_y = get_y_coord(moon_lat, moon_long, moon_radius)
    moon_z = get_z_coord(moon_lat, moon_long)

    dists = [earth_x - moon_x, earth_y - moon_y, earth_z - moon_z]
    range_ = sqrt((dists[0] ** 2) + (dists[1] ** 2) + (dists[2] ** 2))

    rz = dists[0] * cos(moon_lat_rad) * cos(moon_long_rad) + dists[1] * cos(moon_lat_rad) * sin(moon_long_rad) + dists[
        2] * sin(moon_lat_rad)

    elev = asin(rz / range_)

    return rad2deg(elev)


def resize(image_path : str, new_name : str, scale : float) -> str:
    img = Image.open(f'{image_path}')
    resized = img.resize((scale, scale)) # 1/(scale) Scaling

    path = os.getcwd() + f'/Data/Images/{new_name}.png'
    resized.save(path)
    print(f"Created {new_name}.png")
    return path


# Get Start and End Points for AStar Pathfinding
def get_pathfinding_endpoints() -> tuple:
    pygame.init()
    screen_size = [638.5, 638.5]
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Pick Two Points. After that, Press SPACE to Confirm or LEFT_ALT to Reset")

    done = False

    start_pos: tuple | None = None
    goal_pos: tuple | None = None

    heightmap_img = pygame.image.load("Data/Images/interface_overlay.png")
    screen.blit(heightmap_img, (0, 0))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_pos is None:
                    start_pos = pygame.mouse.get_pos()
                    gfxdraw.filled_circle(screen, start_pos[0], start_pos[1], 4, (255, 0, 0))
                    start_pos = (start_pos[0] * 2, start_pos[1] * 2)
                elif goal_pos is None:
                    goal_pos = pygame.mouse.get_pos()
                    gfxdraw.filled_circle(screen, goal_pos[0], goal_pos[1], 4, (255, 0, 0))
                    goal_pos = (goal_pos[0] * 2, goal_pos[1] * 2)

            if start_pos and goal_pos:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pygame.quit()
                        return start_pos, goal_pos
                    elif event.key == pygame.K_LALT:
                        heightmap_img = pygame.image.load("Data/Images/interface_overlay.png")
                        screen.blit(heightmap_img, (0, 0))
                        start_pos, goal_pos = None, None


        pygame.display.flip()




