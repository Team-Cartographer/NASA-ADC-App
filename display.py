from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from utils import get_azi_elev, \
    latitude_from_rect, longitude_from_rect, \
    height_from_rect, slope_from_rect, show_error, load_json, are_you_sure
from random import choice, randint
from a_star import run_astar
from site_manager import check_save
from shutil import move, copytree, rmtree



# Window Declarations and Formatting --------------
app = Ursina(fullscreen=True)
window.set_title('Team Cartographer\'s ADC Application')
window.cog_button.disable()
window.exit_button.color = color.dark_gray

# Load the Save (ESSENTIAL)
save = check_save()
move(src=save.processed_heightmap, dst=os.getcwd() + "/processed_heightmap.png")
copytree(src=save.images_folder, dst=os.getcwd() + "/Images")


def display_quit():
    rmtree(path=os.getcwd() + "/Images")
    move(src=os.getcwd() + '/processed_heightmap.png', dst=save.processed_heightmap)
    print('cleared temporary files and paths')
    print('sys exit confirmed')

    # A little easter egg.
    if randint(1, 10) == 5:
        print('\n\"This is all just a simulation?\"\n\"Always has been.\"')

    exit(0)


window.exit_button.on_click = display_quit


# Display Specific Constants --------------
Y_HEIGHT = 128  # Default Value
SIZE_CONSTANT = save.size
EDITOR_SIZE = 3000
PLAYER_SIZE = 15000
RESET_LOC = (0, 400, 0)  # Default PLAYER Positional Value
VOLUME = 0.15


# Load the Data -----------------
try:
    a_star_data = load_json(save.astar_json)
    info_data = load_json(save.info_json)
except FileNotFoundError:
    show_error("Display Error", "Incorrect Save Selected!")
    exit(1)


# Declaration of Entities --------------

# FirstPersonController Ground Plane
ground_player = Entity(
    model=Terrain(heightmap="/processed_heightmap.png"),
    # color = color.gray,
    texture='Images/moon_surface_texture.png',
    collider='mesh',
    scale=(PLAYER_SIZE, 512, PLAYER_SIZE),
    enabled=False
    )


# EditorCamera Ground Plane
ground_perspective = Entity(
    model=Terrain(heightmap="/processed_heightmap.png"),
    # color=color.gray,
    texture='Images/moon_surface_texture.png',
    collider='box',
    scale=(EDITOR_SIZE, 256, EDITOR_SIZE),
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
    texture='Images/minimap.png',
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
    scale=(0.4, 0.11),
    position=(-0.69, 0.09, 0),
    texture='slopeKey.png',
    enabled=False
)


# Temporarily Disabled
# # Earth Entity (Scales to Player Position)
# earth = Entity(
#    model='sphere',
#    scale=(500, 500, 500),
#    position=(0, 600, 1000),
#    texture='earth_texture.jpg',
#    enabled=True
#    )


credits = Entity(
    parent=camera.ui,
    model='quad',
    scale=(1.75, 1),
    texture='credits.mp4',
    enabled=False
)


# Information Textboxes  -------------
t_lat = Text(text='Latitude:', x=-.54, y=.48, scale=1.1, enabled=False)
t_lon = Text(text='Longitude:', x=-.54, y=.43, scale=1.1, enabled=False)
t_ht = Text(text='Height:', x=-.54, y=.38, scale=1.1, enabled=False)
t_slope = Text(text='Slope:', x=-.54, y=.33, scale=1.1, enabled=False)
t_azi = Text(text='Azimuth:', x=-.54, y=.28, scale=1.1, enabled=False)
t_elev = Text(text='Elevation:', x=-.54, y=.23, scale=1.1, enabled=False)
t_pos = Text(text='positional data', x=-0.883, y=0.185, z=0, enabled=False)
t_song = Text(text=f'Currently Playing: {None}', x=-0.88, y=-0.485, enabled=True, scale=(0.5, 0.5))



# Player Interactable Declarations -------------
sky = Sky()
sky.color = '000000'  # Black

vc = EditorCamera(enabled=False, zoom_speed=2)  # Note: THIS MUST BE INITIALIZED BEFORE <player> OR ZOOMS WON'T WORK.
player = FirstPersonController(position=RESET_LOC, speed=500, mouse_sensitivity=Vec2(25, 25),
                               enabled=False, gravity=False)
player.cursor.scale = 0.00000000001  # Hides the Cursor from the App Display


# Music Functionality --------------
track_list = ['assets/Night_Sky-Petter_Amland.mp3', 'assets/Buffalo-Petter_Amland.mp3.mp3', 'assets/Seraph-Petter_Amland.mp3']
menu_track_list = ['assets/Lonely_Wasteland-John_Bouyer_ft._Natalie_Kwok.mp3', 'OSU!_Pause_Menu_Track.mp3']

run_music = Audio(
    choice(track_list),  # Change this for different tracks.
    volume=VOLUME,
    loop=True,
)
run_music.stop(destroy=False)

pause_music = Audio(
    menu_track_list[1],
    volume=VOLUME,
    loop=True
)
pause_music.stop(destroy=False)

start_menu_music = Audio(
    menu_track_list[0],
    volume=VOLUME,
    loop=True
)


# TODO Add Music Switch Statement
def play_run_music():
    # run_music.clip(choice(track_list))
    t_song.text = f"Currently Playing: {str(run_music.clip).split()[1].replace('_', ' ').replace('.mp3', '')}"
    run_music.play()


# Texture Reloader
def reload_textures():
    textured_entities = [e for e in scene.entities if e.texture]
    reloaded_textures = list()

    for e in textured_entities:
        if str(e.texture.name) == 'credits':
            continue

        if e.texture.name in reloaded_textures:
            continue

        if e.texture.path.parent.name == application.compressed_textures_folder.name:
            # print('texture is made from .psd file', e.texture.path.stem + '.psd')
            texture_importer.compress_textures(e.texture.path.stem)
        # print('reloaded texture:', e.texture.path)
        e.texture._texture.reload()
        reloaded_textures.append(e.texture.name)

    print("reloaded textures")
    return reloaded_textures


# Input Functions and Toggles -------------
def input(key):

    # Reset Player
    if key == 'r':
        player.set_position(RESET_LOC)

    # Slopemap Toggle
    if key == '4':
        ground_player.texture = 'Images/slopemap.png'
        ground_perspective.texture = 'Images/slopemap.png'
        view_cam_player_loc.color = color.green
        color_key.enable()
        color_key.texture = 'slopeKey.png'

    # Heightkey Toggle
    if key == '3':
        ground_player.texture = 'Images/heightkey_surface.png'
        ground_perspective.texture = 'Images/heightkey_surface.png'
        view_cam_player_loc.color = color.white
        color_key.enable()
        color_key.texture = 'heightKey.png'

    if key == '2':
        ground_player.texture = 'Images/AStar_Path.png'
        ground_perspective.texture = 'Images/AStar_Path.png'
        color_key.disable()

    # Moon Texture Toggle (Default)
    if key == '1':
        ground_player.texture = 'Images/moon_surface_texture.png'
        ground_perspective.texture = 'Images/moon_surface_texture.png'
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
        display_quit()

    # Pause
    if key == 'escape' and pause_button.enabled is False and volume_slider.enabled is False and start_button.enabled is False:
        t_song.text = f"Currently Playing: {str(pause_music.clip).split()[1].replace('_', ' ').replace('.mp3', '')}"
        start_menu_music.stop(destroy=True)
        t_lat.disable()
        t_lon.disable()
        t_ht.disable()
        t_azi.disable()
        t_slope.disable()
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
        return_button.enable()
        pause_music.play()
        credits.disable()
        run_music.stop(destroy=False)



# Game Loop Update() Functions -------------

height_vals = ground_player.model.height_values

def update():
    # assets Update
    VOLUME = volume_change()
    pause_music.volume = VOLUME
    start_menu_music.volume = VOLUME
    run_music.volume = VOLUME

    # Map Failsafe
    bound = SIZE_CONSTANT*10/2 - 200
    if -bound > player.position.x or player.position.x > bound or -bound > player.position.z or player.position.z > bound:
        player.set_position(RESET_LOC)

    # Positions
    x, y, z = player.position.x, player.position.y, player.position.z
    player.y = terraincast(player.world_position, ground_player, height_vals) + 60  # Sets correct height

    # Corrected X and Z values for Calculations
    # Note that in Ursina, 'x' and 'z' are the Horizontal (Plane) Axes, and 'y' is vertical.
    nx, nz = int(x / 10 + int(SIZE_CONSTANT/2)), abs(int(z / 10 - int(SIZE_CONSTANT)/2))

    # Updating Position and Viewer Cam Position Labels
    t_pos.text = f'Position: ({int(x)}, {int(y)}, {int(z)})'
    view_cam_player_loc.position = (x / (10 / EDITOR_SIZE), 0, z / (10 / EDITOR_SIZE))

    # Calculating Data
    lat = float(latitude_from_rect(nx, nz, a_star_data))
    long = float(longitude_from_rect(nx, nz, a_star_data))
    slope = slope_from_rect(nx, nz, a_star_data)
    height = height_from_rect(nx, nz, a_star_data)
    azimuth, elevation = get_azi_elev(nx, nz, a_star_data)

    # Updating Variables
    t_lat.text = f'Latitude: {round(lat, 4)}° N'
    t_lon.text = f'Longitude: {round(long, 4)}° E'
    t_ht.text = 'Height: ' + str(height) + 'm'
    t_slope.text = 'Slope: ' + str(slope) + '°'
    t_azi.text = 'Azimuth: ' + str(round(azimuth, 4)) + '°'
    t_elev.text = 'Elevation: ' + str(round(elevation, 4)) + '°'

    # Sprint Key
    if held_keys['left shift']:
        player.speed = 1250
    else:
        player.speed = 500

    # Mini-Map Dot Positioning
    mmsc: int = SIZE_CONSTANT * PLAYER_SIZE  # minimap size constant
    mx, mz = (x/mmsc) + 0.5, (z/mmsc) - 0.5
    mini_dot.position = (mx, mz, 0)

    # # Earth Positioning (haha funny number)
    # earth.position = (earth.x, 420+elevation*100, earth.z)
    # if view_cam_player_loc.enabled is True:
    #     earth.z = -4000
    # else:
    #     earth.z = -9000


# All Button Functions --------------
def start_game():
    ground_player.enable()
    player.enable()
    start_button.disable()
    t_lat.enable()
    t_lon.enable()
    t_ht.enable()
    t_azi.enable()
    t_slope.enable()
    t_elev.enable()
    t_start_menu.disable()
    t_start_menu_creds.disable()
    minimap.enable()
    mini_dot.enable()
    t_pos.enable()
    repath_button.disable()
    launch_button.disable()
    t_current_site.disable()
    volume_slider.disable()
    sens_slider.disable()
    play_run_music()
    pause_music.stop(destroy=False)

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
    t_elev.enable()
    t_start_menu.disable()
    t_quit.disable()
    minimap.enable()
    mini_dot.enable()
    t_pos.enable()
    return_button.disable()
    pause_music.stop(destroy=False)
    play_run_music()

def main_menu_returner():
    t_song.text = f"Currently Playing: {str(pause_music.clip).split()[1].replace('_', ' ').replace('.mp3', '')}"
    t_start_menu.disable(), t_start_menu_creds.disable(), start_button.disable()
    creds_button.disable()
    start_menu_music.stop(destroy=False)
    t_current_site.enable()
    launch_button.enable()
    repath_button.enable()
    pause_button.disable()
    t_quit.disable()
    t_pause.disable()
    return_button.disable()
    pause_music.play()
    volume_slider.enable()
    sens_slider.enable()

def creds_init():
    start_menu_music.stop(destroy=False)
    t_start_menu.disable()
    t_start_menu_creds.disable()
    start_button.disable()
    credits.enable()
    creds_button.disable()
    start_menu_music.play()

def repath_init():
    try:
        run_astar(save)
        reload_textures()
    except TypeError:
        if are_you_sure("A* exited early", "There was a problem with A*. Click OK to run again"):
            repath_init()


# Slider Functions --------------
def volume_change():
    return volume_slider.value

def sens_change():
    sens = sens_slider.value * 65 # Sensitivity Scaler
    player.mouse_sensitivity = Vec2(sens, sens)


# UI Text and Buttons --------------

# Start Menu
t_start_menu = Text(text="Welcome to Team Cartographer's 2023 NASA ADC Application", x=-0.35, y=0.08)
t_start_menu_creds = Text(text="https://github.com/abhi-arya1/NASA-ADC-App \n \n      https://github.com/pokepetter/ursina", x=-0.275, y=-0.135, color=color.dark_gray)
start_button = Button(text='Main Menu', color=color.gray, highlight_color=color.dark_gray, scale=(0.2, 0.05), y=-0.01, on_click=main_menu_returner)
creds_button = Button(text='Credits', color=color.gray, highlight_color=color.dark_gray, scale=(0.2, 0.05), y=-0.07, on_click=creds_init)

# For Main Menu
t_current_site = Text(text=f"Currently Visiting: {save.site_name}", x=-0.2, y=0.1, scale=1.25, enabled=False)
launch_button = Button(text="Visualize Site",  color=color.gray, highlight_color=color.dark_gray,
                       scale=(0.25, 0.06), x=0, y=0.0, enabled=False, on_click=start_game)
repath_button = Button(text="Re-Run Pathfinding", color=color.dark_gray, highlight_color=Color(0.15, 0.15, 0.15, 1.0),
                       scale=(0.25, 0.06), x=0, y=-0.08, enabled=False, on_click=repath_init)
volume_slider = ThinSlider(text='Volume', value=0.15, dynamic=True, on_value_changed=volume_change, enabled=False, x=-0.23, y=-0.2)
sens_slider = ThinSlider(text='Sensitivity', value=0.5, dynamic=True, on_value_changed=sens_change, enabled=False, x=-0.23, y=-0.27)

# Pause Menu Text and Buttons
t_pause = Text(text="You are Currently Paused...", x=-0.16, y=0.08, enabled=False)
pause_button = Button(text='Click to Unpause', color=color.gray, highlight_color=color.dark_gray,
                      scale=(0.23, 0.05), enabled=False, on_click=on_unpause)
t_quit = Text(text="Press 'LShift+Q' to quit.", x=-0.14, y=-0.135, enabled=False)
return_button = Button(text='Main Menu', color=color.gray, highlight_color=color.dark_gray,
                       scale=(0.23, 0.06), enabled=False, x=0, y=-0.07, on_click=main_menu_returner)



# Runs display.py -------------
if randint(1, 10) == 5:
    print("\n\"All alone in this universe...\"\n")

t_song.text = f"Currently Playing: {str(start_menu_music.clip).split()[1].replace('_', ' ').replace('.mp3', '')}"
input_handler.rebind("f", "k")  # Gets rid of EditorCamera Input Issue
app.run(info=False)

