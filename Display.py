import FileManager as fm
from ursina import *
from utils import get_azi_elev, \
    latitude_from_rect, longitude_from_rect, \
    get_radius, height_from_rect, slope_from_rect
from ursina.prefabs.first_person_controller import FirstPersonController

# Window Declarations and Formatting -------------
app = Ursina()
window.set_title('Team Cartographer\'s ADC Application')
window.cog_button.disable()
window.exit_button.color = color.dark_gray

# Display Specific Constants -------------
Y_HEIGHT = 128  # Default Value
SIZE_CONSTANT = fm.get_size_constant()
EDITOR_SCALE_FACTOR = 3
PLAYER_SCALE_FACTOR = 8
RESET_LOC = (0, Y_HEIGHT*PLAYER_SCALE_FACTOR, 0)  # Default PLAYER Positional Value



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


# Declaration of Entities -------------

# FirstPersonController Ground Plane
ground_player = Entity(
    model=Terrain(heightmap='processed_heightmap.png'),
    texture='moon_surface_texture.png',
    collider='box',
    scale=(SIZE_CONSTANT*10, Y_HEIGHT*PLAYER_SCALE_FACTOR, SIZE_CONSTANT*10),
    enabled=False
    )

# EditorCamera Ground Plane
ground_perspective = Entity(
    model=Terrain(heightmap='processed_heightmap.png'),
    texture='moon_surface_texture.png',
    collider='box',
    scale=(SIZE_CONSTANT*3, Y_HEIGHT*EDITOR_SCALE_FACTOR, SIZE_CONSTANT*3),
    enabled=False
    )

# ViewCamera Player Location Beacon
view_cam_player_loc = Entity(
    model='cube',
    scale=(20, 1000, 20),
    color=color.red,
    enabled=False,
    )

# Minimap Image
minimap = Entity(
    parent=camera.ui,
    center=(0, 0, 0),
    model="quad",
    scale=(0.3, 0.3),
    origin=(-0.5, 0.5),
    position=window.top_left,
    texture='minimap.png',
    enabled=False
    )

# Minimap Dot Entity
mini_dot = Entity(
    parent=minimap,
    model='circle',
    scale=(0.03, 0.03),
    position=(0, 0, 0),
    color=color.red,
    enabled=False
    )

# Color Key Entity (Activates on Heightmap/Slopemap Toggle)
color_key = Entity(
    parent=camera.ui,
    model='quad',
    scale = (0.3, 0.11),
    position=(-0.74, 0.09, 0),
    texture='slopeKey.png',
    enabled=False
)

# Earth Entity (Scales to Player Position)
#earth = Entity(
#    model='sphere',
#    scale=(1000, 1000, 1000),
#    position=(0, 600, -9000),
#    texture='earth_texture.jpg',
#    enabled=True
#    )


# Slope and Height Toggle Image Pathing -------------
slopemap = fm.parent_path + '/slopemap.png'
heightkey = fm.parent_path + '/heightkey_surface.png'



# Textboxes  -------------
t_lat = Text(text='Latitude:', x=-.54, y=.48, scale=1.1, enabled=False)
t_lon = Text(text='Longitude:', x=-.54, y=.43, scale=1.1, enabled=False)
t_ht = Text(text='Height:', x=-.54, y=.38, scale=1.1, enabled=False)
t_slope = Text(text='Slope:', x=-.54, y=.33, scale=1.1, enabled=False)
t_azi = Text(text='Azimuth:', x=-.54, y=.28, scale=1.1, enabled=False)
t_elev = Text(text='Elevation:', x=-.54, y=.23, scale=1.1, enabled=False)
t_pos = Text(text='positional data', x=-0.883, y=0.185, z=0, enabled=False)
t_info = Text(
    #text='M for Moon, L for Slopemap, H for Heightmap, Esc for Pause, X for Switch',
    text='',
    x=-.15, y=-.45, scale=1.1, color=color.black, enabled=False)



# Player Interactable Declarations -------------

sky = Sky()
sky.color = '000000' # Black

vc = ViewCamera(enabled=False, zoom_speed=5, rotation_x=32.421871185302734, rotation_y=-26.388877868652344, hotkeys={}) # Note: THIS MUST BE INITIALIZED BEFORE <player> OR ZOOMS WON'T WORK.

player = FirstPersonController(position=RESET_LOC, speed=500, mouse_sensitivity=Vec2(25, 25), enabled=False, gravity=False)
#player.scale = (0.5, 1, 0.5)
player.cursor.scale = 0.00000000001 # Hides the Cursor from the App Display




# Input Functions and Toggles -------------
def input(key):

    # Reset Player
    if key == 'r':
        player.set_position(RESET_LOC)

    # Slopemap Toggle
    if key == 'l':
        ground_player.texture = 'slopemap.png'
        ground_perspective.texture = 'slopemap.png'
        view_cam_player_loc.color = color.blue
        color_key.enable()
        color_key.texture='slopeKey.png'

    # Heightkey Toggle
    if key == 'h':
        ground_player.texture = 'heightkey_surface.png'
        ground_perspective.texture = 'heightkey_surface.png'
        view_cam_player_loc.color = color.white
        color_key.enable()
        color_key.texture='heightKey.png'

    if key == 'p':
        ground_player.texture = 'AStar_Path.png'
        ground_perspective.texture = 'AStar_Path.png'
        color_key.disable()

    # Moon Texture Toggle (Default)
    if key == 'm':
        ground_player.texture = 'moon_surface_texture.png'
        ground_perspective.texture = 'moon_surface_texture.png'
        view_cam_player_loc.color = color.red
        color_key.disable()

    # Toggle between Player and EditorCamera
    if key == 'x' and start_button.enabled is False:
        player.enabled = not player.enabled
        vc.enabled = not vc.enabled
        ground_player.enabled = not ground_player.enabled
        ground_perspective.enabled = not ground_perspective.enabled
        view_cam_player_loc.enabled = not view_cam_player_loc.enabled

    # Quit App
    if held_keys['left shift', 'q']:
        exit(0)

    # Pause
    if key == 'escape' and pause_button.enabled is False:
        t_lat.disable()
        t_lon.disable()
        t_ht.disable()
        t_azi.disable()
        t_slope.disable()
        t_info.disable()
        t_elev.disable()
        player.disable()
        vc.disable()
        ground_player.disable()
        ground_perspective.disable()
        view_cam_player_loc.disable()
        minimap.disable()
        mini_dot.disable()
        t_pos.disable()
        pause_button.enable()
        t_pause.enable()
        t_quit.enable()
        color_key.disable()
        open_save_button.enable()
        #github_button.enable()


height_vals = ground_player.model.height_values


# Game Loop Update() Functions -------------
def update():
    # Map Failsafe
    if -6150 > player.position.x or player.position.x > 6150 or -6150 > player.position.z or player.position.z > 6150:
        player.set_position(RESET_LOC)

    # Positions
    x, y, z = player.position.x, player.position.y, player.position.z
    player.y = terraincast(player.world_position, ground_player, height_vals) + 35 # Sets correct height

    #origin = (x, y+2, z)
    #hit_info = raycast(origin=origin, direction=(0,0,-1), distance=1, traverse_target=ground_player, ignore=list(), debug=False)
    #if hit_info:
    #    print('hit')

    # Corrected X and Z values for Calculations
    # Note that in Ursina, 'x' and 'z' are the Horizontal (Plane) Axes, and 'y' is vertical.
    nx, nz = int(x / 10 + 638), abs(int(z / 10 - 638))

    # Updating Position and Viewer Cam Position Labels
    t_pos.text = f'Position: ({int(x)}, {int(y)}, {int(z)})'
    view_cam_player_loc.position = (x / (10 / 3), 0, z / (10 / 3))

    # Calculating Data
    rad = get_radius(nx, nz)
    lat = float(latitude_from_rect(nx, nz, rad))
    long = -float(longitude_from_rect(nx, nz, rad))
    slope = slope_from_rect(nx, nz)
    height = height_from_rect(nx, nz)
    azimuth, elevation = get_azi_elev(nx, nz)

    # Updating Variables
    t_lat.text = f'Latitude: {round(lat, 4)}° S'
    t_lon.text = f'Longitude: {round(long, 4)}° E'
    t_ht.text = 'Height: ' + str(height) + 'm'
    t_slope.text = 'Slope: ' + str(slope) + '°'
    t_azi.text = 'Azimuth: ' + str(round(azimuth, 4)) + '°'
    t_elev.text = 'Elevation: ' + str(round(elevation, 4)) + '°'

    # Sprint Key
    if held_keys['left shift']:
        player.speed = 1500
    else:
        player.speed = 500


    # Mini-Map Dot Positioning
    mx, mz = (x/12770) + 0.5, (z/12770)-0.5
    mini_dot.position = (mx, mz, 0)

    # Earth Positioning
    #earth.position = (earth.x, 400*(elevation), earth.z)



# Create Start Menu -------------
def start_game():
    ground_player.enable()
    player.enable()
    start_button.disable()
    t_lat.enable()
    t_lon.enable()
    t_ht.enable()
    t_azi.enable()
    t_slope.enable()
    t_info.enable()
    t_elev.enable()
    t_start_menu.disable()
    t_start_menu_creds.disable()
    minimap.enable()
    mini_dot.enable()
    t_pos.enable()


# Unpause Button Function -------------
def on_unpause():
    if str(ground_player.texture) == 'heightkey_surface.png' or str(ground_player.texture) == 'slopemap.png':
        color_key.enable()

    ground_player.enable()
    player.enable()
    pause_button.disable()
    t_pause.disable()
    t_lat.enable()
    t_lon.enable()
    t_ht.enable()
    t_azi.enable()
    t_slope.enable()
    t_info.enable()
    t_elev.enable()
    t_start_menu.disable()
    t_quit.disable()
    minimap.enable()
    mini_dot.enable()
    t_pos.enable()
    open_save_button.disable()



# Start Menu Text and Buttons -------------
t_start_menu = Text(text="Welcome to Team Cartographer's 2023 NASA ADC Application", x=-0.35, y=0.08)
t_start_menu_creds = Text(text="https://github.com/abhi-arya1/NASA-ADC-App \n \n      https://github.com/pokepetter/ursina", x=-0.275, y=-0.07, color=color.dark_gray)
start_button = Button(text='Click to Begin', color=color.gray, highlight_color=color.dark_gray, scale=(0.2, 0.05))
start_button.on_click = start_game


# Pause Menu Text and Buttons -------------
t_pause = Text(text="You are Currently Paused...", x=-0.16, y=0.08, enabled=False)
pause_button = Button(text='Click to Unpause', color=color.gray, highlight_color=color.dark_gray, scale=(0.23, 0.05), enabled=False)
t_quit = Text(text="Press 'LShift+Q' to quit.", x=-0.14, y=-0.06, enabled=False)
pause_button.on_click = on_unpause

open_save_button = Button(text='Load Previous Save', color=color.gray, highlight_color=color.dark_gray, scale=(0.25, 0.06), enabled=False, x=0, y=-0.15)
def open_save():
    import tkinter as tk
    from tkinter.filedialog import askdirectory
    root = tk.Tk()
    root.withdraw()
    save_folder = askdirectory()
    # fm.load_save(save_folder) # Proof of Concept Shtuff
    #print(filename) # For testing

open_save_button.on_click = open_save


# Runs Display.py -------------
if __name__ == '__main__':
    app.run(info=False)
