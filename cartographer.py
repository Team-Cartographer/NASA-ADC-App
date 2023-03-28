from PIL import Image
from utils import resize, get_specific_from_json
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from os import getcwd
from shutil import move
from time import time
import random
from file_manager import FileManager


fm = FileManager()

Image.MAX_IMAGE_PIXELS = None


def sns_heatmap(arr, cmap, save):
    start_time = time()

    # cmap reference: https://matplotlib.org/stable/gallery/color/colormap_reference.html

    sns.heatmap(arr, square=True, cbar=False, xticklabels=False,
                yticklabels=False, cmap=cmap)
    plt.tight_layout()
    plt.savefig(save, dpi=2048, transparent=True, format='png', bbox_inches='tight', pad_inches=0)

    # Convert to RGBA for Ursina.
    print(f'{save} created in {round(time()-start_time, 2)}s')


heights = get_specific_from_json(8, fm.astar_json_path)
slopes = get_specific_from_json(3, fm.astar_json_path)


def create_surface_texture():
    texture = Image.new("RGBA", (fm.size, fm.size))
    for y in tqdm(range(len(slopes)), desc='Creating Surface Texture'):
        for x in range(len(slopes[y])):
            color = 255
            # color logic here
            for i in range(int(slopes[y][x])):
                color -= random.randint(2, 5)
            texture.putpixel((x, y), (color, color, color))
    texture.save(fm.texture_path)


# Creates RAW_Heightmap, Slopemap, and Heightkey
def draw_all():

    # Creates Heightmap for Ursina
    sns_heatmap(
        arr=heights,
        cmap="gist_gray",
        save=fm.raw_height_map_path
    )

    # Creates Heightkey
    # TODO Add Reduced Opacity Feature to Original Texture for this
    sns_heatmap(
        arr=heights,
        cmap='viridis',
        save=fm.surface_heightkey_path
    )

    # Creates Slopemap
    sns_heatmap(
        arr=slopes,
        cmap='inferno',
        save=fm.slopemap_path
    )

    # Creates Surface Texture
    create_surface_texture()


def draw_path(path, image, color):
    for i in tqdm(range(len(path)), desc="Drawing A* Path"):
        image.putpixel(path[0], path[1], color)
        print(f"\rCreating Path Image. {round(i / len(path), 4)}% complete", end="")
    return image


if __name__ == "__main__":

    start = time()

    # Create the essential images.
    draw_all()

    # Image Scaling for Faster Ursina Runs, as well as proper dimensions.
    proper_heightmap = resize(
        image_path=fm.raw_height_map_path,
        new_name='processed_heightmap',
        scale=128,
        transpose=True
    )
    move(fm.processed_heightmap_path, getcwd() + '/processed_heightmap.png')

    proper_surface_texture = resize(
        image_path=fm.texture_path,
        new_name='moon_surface_texture',
        scale=fm.size,
        transpose=True
    )

    flipped_slopemap = resize(
        image_path=fm.slopemap_path,
        new_name='slopemap',
        scale=fm.size,
        transpose=True
    )

    flipped_heightmap = resize(
        image_path=fm.surface_heightkey_path,
        new_name='heightkey_surface',
        scale=fm.size,
        transpose=True
    )

    minimap = resize(
        image_path=fm.texture_path,
        new_name='minimap',
        scale=128
    )

    interface_slopemap = resize(
        image_path=fm.slopemap_path,
        new_name='interface_slopemap',
        scale=500
    )

    interface_texture = resize(
        image_path=fm.texture_path,
        new_name='interface_texture',
        scale=500
    )

    interface_heightkey = resize(
        image_path=fm.surface_heightkey_path,
        new_name='interface_heightkey',
        scale=500
    )

    print(f'Cartographer ran in {round(time()-start, 2)}s')



