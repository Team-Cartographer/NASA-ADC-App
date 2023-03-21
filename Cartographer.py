import FileManager as fm
from PIL import Image
from utils import resize, get_specific_from_json
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from os import getcwd
from shutil import move
from time import time

max_z = fm.get_max_height()
CALCULATION_CONS = 255 / max_z
ONE_THIRD = 1 / 3
TWO_THIRDS = 2 / 3
SIZE_CONSTANT = fm.get_size_constant()

Image.MAX_IMAGE_PIXELS = None


def sns_heatmap(arr, cmap, save):
    start = time()

    # cmap reference: https://matplotlib.org/stable/gallery/color/colormap_reference.html

    sns.heatmap(arr, square=True, cbar=False, xticklabels=False,
                yticklabels=False, cmap=cmap)
    plt.tight_layout()
    plt.savefig(save, dpi=2048, transparent=True, format='png', bbox_inches='tight')

    # Convert to RGBA for Ursina.
    #Image.open(save).convert('RGBA').save(save)
    print(f'{save} created in {round(time()-start, 2)}s')

heights = get_specific_from_json(8, fm.data_path + "/AStarRawData.json")
slopes = get_specific_from_json(3, fm.data_path + "/AStarRawData.json")

# Creates RAW_Heightmap, Slopemap, and Heightkey
def draw_all():

    # Create Texture
    sns_heatmap(
        arr=slopes,
        cmap="gist_gray_r",
        save= fm.images_path + '/moon_surface_texture.png'
    )

    # Create Heightmap for Ursina
    sns_heatmap(
        arr=heights,
        cmap="gist_gray",
        save=fm.images_path + '/RAW_heightmap.png'
    )

    # Create Heightkey
    #TODO Add Reduced Opacity Feature to Original Texture for this
    sns_heatmap(
        arr=heights,
        #cmap="gist_rainbow_r",
        cmap='viridis',
        save=fm.images_path + '/heightkey_surface.png'
    )

    # Create Slopemap
    sns_heatmap(
        arr=slopes,
        #cmap="gist_rainbow_r",
        cmap='inferno',
        save=fm.images_path + '/slopemap.png'
    )


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
    downscaled = resize(
        image_path=fm.images_path + '/RAW_heightmap.png',
        new_name='processed_heightmap',
        scale=128,
        transpose=True
    )
    move(fm.images_path + '/processed_heightmap.png', getcwd() + '/processed_heightmap.png')

    proper_surface_texture = resize(
        image_path='Data/Images/moon_surface_texture.png',
        new_name='moon_surface_texture',
        scale=1277,
        transpose=True
    )

    flipped_slopemap = resize(
        image_path='Data/Images/slopemap.png',
        new_name='slopemap',
        scale=1277,
        transpose=True
    )

    flipped_heightmap = resize(
        image_path='Data/Images/heightkey_surface.png',
        new_name='heightkey_surface',
        scale=1277,
        transpose=True
    )

    minimap = resize(
        image_path='Data/Images/moon_surface_texture.png',
        new_name='minimap',
        scale=127
    )

    interface_slopemap = resize(
        image_path='Data/Images/slopemap.png',
        new_name='interface_slopemap',
        scale=500
    )

    interface_texture = resize(
        image_path='Data/Images/moon_surface_texture.png',
        new_name='interface_texture',
        scale=500
    )

    interface_heightkey = resize(
        image_path='Data/Images/heightkey_surface.png',
        new_name='interface_heightkey',
        scale=500
    )

    print(f'{round(time()-start, 2)}s taken.')



