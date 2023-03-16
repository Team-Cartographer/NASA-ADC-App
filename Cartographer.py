import FileManager as fm
from ast import literal_eval
from PIL import Image
from utils import file2list, resize
from tqdm import tqdm

astar_data_path = fm.data_path + "/AStarRawData.csv"
full_list = file2list(astar_data_path)

max_z = fm.get_max_z()
CALCULATION_CONS = 255 / max_z
ONE_THIRD = 1/3
TWO_THIRDS = 2/3
SIZE_CONSTANT = fm.get_size_constant()


def calculate_color(height):
    color = 255 - (height * CALCULATION_CONS)
    return int(color), int(color), int(color)

def calc_rgb_color(height):
    r, g, b = 0, 0, 0
    if height <= ONE_THIRD * max_z:
        b = height * CALCULATION_CONS
    elif height <= TWO_THIRDS * max_z:
        g = height * CALCULATION_CONS
    else:
        r = height * CALCULATION_CONS
    return int(r), int(g), int(b)

# Creates RAW_Heightmap, Slopemap, and Heightkey
def draw_all():
    for i in tqdm(range(len(full_list)), desc="Creating All Images"):
        for j in range(len(full_list[i])):
            slope = float(literal_eval(full_list[j][i])[3])
            height = float(literal_eval(full_list[j][i])[2])

            slope_color = (255, 0, 0)
            if slope < 20:
                slope_color = (255, 255, 0)
            if slope < 8:
                slope_color = (0, 255, 0)

            heightkey_color = calc_rgb_color(height)

            heightmap_color = calculate_color(height)

            heightmap.putpixel((j, i), heightmap_color)
            slopemap.putpixel((j, i), slope_color)
            heightkey.putpixel((j, i), heightkey_color)


def draw_path(path, image, color):
    for i in tqdm(range(len(path)), desc="Drawing A* Path"):
        image.putpixel(path[0], path[1], color)
        print(f"\rCreating Path Image. {round(i / len(path), 4)}% complete", end="")
    return image


if __name__ == "__main__":

    heightmap = Image.new('RGBA', (SIZE_CONSTANT, SIZE_CONSTANT), 'blue')
    slopemap = Image.new('RGBA', (SIZE_CONSTANT, SIZE_CONSTANT), 'blue')
    heightkey = Image.new('RGBA', (SIZE_CONSTANT, SIZE_CONSTANT), 'blue')

    draw_all() # "Magic Function" - Efe

    heightmap.save(fm.images_path + '/RAW_heightmap.png')  # must save here for a proper read from Ursina
    slopemap.save(fm.images_path + '/slopemap.png')
    heightkey.save(fm.images_path + '/heightkey_surface.png')

    # Image Scaling for Faster Ursina Runs
    downscaled = resize(
        image_path=fm.images_path + '/RAW_heightmap.png',
        new_name='processed_heightmap', 
        scale=81
    )

    minimap = resize(
        image_path='moon_surface_texture.png', 
        new_name='minimap',
        scale=127
    )
    
    astar_texture = resize(
        image_path='moon_surface_texture.png', 
        new_name='AStar_Texture',
        scale=1277
    )

    interface_slopemap = resize(
        image_path='Data/Images/slopemap.png',
        new_name='interface_slopemap',
        scale=500
    )

    interface_texture = resize(
        image_path='moon_surface_texture.png',
        new_name='interface_texture',
        scale=500
    )

    interface_heightkey = resize(
        image_path='Data/Images/heightkey_surface.png',
        new_name='interface_heightkey',
        scale=500
    )

    print("Cartographer Success")
