from __future__ import annotations
import csv
import tkinter as tk
from tkinter import messagebox
import os
from numpy import rad2deg, deg2rad
from math import atan2, sin, cos, asin, sqrt
from ast import literal_eval
from PIL import Image  # of deez nuts (sorry)
import pygame
from pygame import gfxdraw
from webbrowser import open as open_page
from ursina import *


def file2list(path):
    with open(path) as csv_file:
        new_list = list(csv.reader(csv_file, delimiter=','))
        csv_file.close()

    return new_list


try:
    astar_list = file2list(os.getcwd() + '/Data/AStarRawData.csv')
except FileNotFoundError:
    pass


def open_webpage(url: str) -> None:
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
    return sqrt((x ** 2) + (y ** 2))


def latitude_from_rect(x: float, y: float, radius: float) -> float:
    # lat, _, _ = (radius/(30366 + (1/9))) - 90, x, y
    lat = literal_eval(astar_list[x][y])[6]
    return lat


def longitude_from_rect(x: float, y: float, radius: float) -> float:
    # long, _ = rad2deg(arccos(x/radius)), y
    long = literal_eval(astar_list[x][y])[7]
    return long


def slope_from_rect(x: float, y: float) -> float:
    return literal_eval(astar_list[x][y])[3]


def height_from_rect(x: float, y: float) -> float:
    height = float(os.getenv("MAX_Z")) - literal_eval(astar_list[x][y])[2]
    return height


def get_x_coord(lat, long, rad):  # takes in degrees latitude and longitude
    return rad * cos(deg2rad(lat)) * cos(deg2rad(long))


def get_y_coord(lat, long, rad):
    return rad * cos(deg2rad(lat)) * sin(deg2rad(long))


def get_z_coord(lat, rad):
    return rad * sin(deg2rad(lat))


# ONLY FOR USE WITH Display.py
def get_azi_elev(x, y):
    data = literal_eval(astar_list[x][y])
    return round(data[4], 5), round(data[5], 5)  # azimuth and elevation, respectively


def get_azimuth(moon_lat, moon_long):
    """
    Gets Azimuth based on Latitude and Longitude for DataProcessor

    Keyword arguments:\n
    moon_lat -- latitude of Player pos. in Display.py
    moon_long -- longitude of Player pos. in Display.py
    """

    # True Lunar South Pole
    lunar_south_pole_lat, lunar_south_pole_long = deg2rad(-89.54), deg2rad(0)
    moon_lat_radian = deg2rad(moon_lat)
    moon_long_radian = deg2rad(moon_long)

    # Azimuth Calculation
    c1 = sin(moon_long_radian - lunar_south_pole_long) * cos(moon_lat_radian)
    c2 = (cos(lunar_south_pole_lat) * sin(moon_lat_radian)) - (
                sin(lunar_south_pole_lat) * cos(moon_lat_radian) * cos(moon_long_radian - lunar_south_pole_long))
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


def resize(image_path: str, new_name: str, scale: float) -> str:
    img = Image.open(f'{image_path}')
    resized = img.resize((scale, scale))  # 1/(scale) Scaling

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


# Ursina EditorCamera Retrofit Implementation for Display (DO NOT EDIT)
class ViewCamera(Entity):

    def __init__(self, **kwargs):
        camera.editor_position = camera.position
        super().__init__(name='editor_camera', eternal=False)

        # self.gizmo = Entity(parent=self, model='sphere', color=color.orange, scale=.025, add_to_scene_entities=False, enabled=False)

        self.rotation_speed = 200
        self.pan_speed = Vec2(5, 5)
        self.move_speed = 10
        self.zoom_speed = 1.25
        self.zoom_smoothing = 8
        self.rotate_around_mouse_hit = False

        self.smoothing_helper = Entity(add_to_scene_entities=False)
        self.rotation_smoothing = 0
        self.look_at = self.smoothing_helper.look_at
        self.look_at_2d = self.smoothing_helper.look_at_2d
        self.rotate_key = 'right mouse'

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.start_position = self.position
        self.perspective_fov = camera.fov
        self.orthographic_fov = camera.fov
        self.on_destroy = self.on_disable
        # Removed toggle hotkeys for EditorCamera
        self.hotkeys = {} #{'toggle_orthographic':'shift+p', 'focus':'f', 'reset_center':'shift+f'}


    def on_enable(self):
        camera.org_parent = camera.parent
        camera.org_position = camera.position
        camera.org_rotation = camera.rotation
        camera.parent = self
        camera.position = camera.editor_position
        camera.rotation = (0,0,0)
        self.target_z = camera.z
        self.target_fov = camera.fov


    def on_disable(self):
        camera.editor_position = camera.position
        camera.parent = camera.org_parent
        camera.position = camera.org_position
        camera.rotation = camera.org_rotation


    def on_destroy(self):
        destroy(self.smoothing_helper)


    def input(self, key):
        combined_key = ''.join(e+'+' for e in ('control', 'shift', 'alt') if held_keys[e] and not e == key) + key
        '''
        if combined_key == self.hotkeys['toggle_orthographic']:
            if not camera.orthographic:
                self.orthographic_fov = camera.fov
                camera.fov = self.perspective_fov
            else:
                self.perspective_fov = camera.fov
                camera.fov = self.orthographic_fov

            camera.orthographic = not camera.orthographic


        elif combined_key == self.hotkeys['reset_center']:
            self.animate_position(self.start_position, duration=.1, curve=curve.linear)

        elif combined_key == self.hotkeys['focus'] and mouse.world_point:
            self.animate_position(mouse.world_point, duration=.1, curve=curve.linear)
        '''

        if key == 'scroll up':
            if not camera.orthographic:
                target_position = self.world_position
                # if mouse.hovered_entity and not mouse.hovered_entity.has_ancestor(camera):
                #     target_position = mouse.world_point

                self.world_position = lerp(self.world_position, target_position, self.zoom_speed * time.dt * 10)
                self.target_z += self.zoom_speed * (abs(self.target_z)*.1)
            else:
                self.target_fov -= self.zoom_speed * (abs(self.target_fov)*.1)
                self.target_fov = clamp(self.target_fov, 1, 200)

        elif key == 'scroll down':
            if not camera.orthographic:
                # camera.world_position += camera.back * self.zoom_speed * 100 * time.dt * (abs(camera.z)*.1)
                self.target_z -= self.zoom_speed * (abs(self.target_z)*.1)
            else:
                self.target_fov += self.zoom_speed * (abs(self.target_fov)*.1)
                self.target_fov = clamp(self.target_fov, 1, 200)

        elif key == 'right mouse down' or key == 'middle mouse down':
            if mouse.hovered_entity and self.rotate_around_mouse_hit:
                org_pos = camera.world_position
                self.world_position = mouse.world_point
                camera.world_position = org_pos



    def update(self):
        if held_keys['gamepad right stick y'] or held_keys['gamepad right stick x']:
            self.smoothing_helper.rotation_x -= held_keys['gamepad right stick y'] * self.rotation_speed / 100
            self.smoothing_helper.rotation_y += held_keys['gamepad right stick x'] * self.rotation_speed / 100

        elif held_keys[self.rotate_key]:
            self.smoothing_helper.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.smoothing_helper.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.direction = Vec3(
                self.forward * (held_keys['w'] - held_keys['s'])
                + self.right * (held_keys['d'] - held_keys['a'])
                + self.up    * (held_keys['e'] - held_keys['q'])
                ).normalized()

            self.position += self.direction * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            if self.target_z < 0:
                self.target_z += held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt
            else:
                self.position += camera.forward * held_keys['w'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

            self.target_z -= held_keys['s'] * (self.move_speed + (self.move_speed * held_keys['shift']) - (self.move_speed*.9 * held_keys['alt'])) * time.dt

        if mouse.middle:
            if not camera.orthographic:
                zoom_compensation = -self.target_z * .1
            else:
                zoom_compensation = camera.orthographic * camera.fov * .2

            self.position -= camera.right * mouse.velocity[0] * self.pan_speed[0] * zoom_compensation
            self.position -= camera.up * mouse.velocity[1] * self.pan_speed[1] * zoom_compensation

        if not camera.orthographic:
            camera.z = lerp(camera.z, self.target_z, time.dt*self.zoom_smoothing)
        else:
            camera.fov = lerp(camera.fov, self.target_fov, time.dt*self.zoom_smoothing)

        if self.rotation_smoothing == 0:
            self.rotation = self.smoothing_helper.rotation
        else:
            self.quaternion = slerp(self.quaternion, self.smoothing_helper.quaternion, time.dt*self.rotation_smoothing)
            camera.world_rotation_z = 0


    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if hasattr(self, 'smoothing_helper') and name in ('rotation', 'rotation_x', 'rotation_y', 'rotation_z'):
            setattr(self.smoothing_helper, name, value)
