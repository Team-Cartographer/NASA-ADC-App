import FileManager as fm
from PIL import Image
from utils import resize, timeit, get_specific_from_json
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from os import getcwd
from shutil import move
import random

max_z = fm.get_max_height()
min_z = fm.get_min_height()
CALCULATION_CONS = 255 / max_z
ONE_THIRD = 1 / 3
TWO_THIRDS = 2 / 3
SIZE_CONSTANT = fm.get_size_constant()


def calculate_color(height):
    color = 255 - (height * CALCULATION_CONS)
    return int(color), int(color), int(color)


@timeit
def sns_heatmap(arr, cmap, save):
    # cmap reference: https://matplotlib.org/stable/gallery/color/colormap_reference.html

    sns.heatmap(arr, square=True, cbar=False, xticklabels=False,
                yticklabels=False, cmap=cmap)
    plt.savefig(save, dpi=2048, transparent=True, format='png', bbox_inches='tight')

    # Convert to RGBA for Ursina.
    Image.open(save).convert('RGBA').save(save)
    print(f'{save} created.')


# Creates RAW_Heightmap, Slopemap, and Heightkey
@timeit
def draw_all():
    # # Create Heightmap for Ursina
    # sns_heatmap(
    #     arr=get_specific_from_json(8, fm.data_path + "/AStarRawData.json"),
    #     cmap="gist_gray",
    #     save=fm.images_path + '/RAW_heightmap.png'
    # )
    #
    # # Create Heightkey
    # sns_heatmap(
    #     arr=get_specific_from_json(8, fm.data_path + "/AStarRawData.json"),
    #     cmap="gist_rainbow_r",
    #     save=fm.images_path + '/heightkey_surface.png'
    # )
    #
    # Create Slopemap
    # sns_heatmap(
    #     arr=get_specific_from_json(3, fm.data_path + "/AStarRawData.json"),
    #     cmap="gist_rainbow_r",
    #     save=fm.images_path + '/slopemap.png'
    # )

    # Create Slopemap
    sns_heatmap(
        arr=get_specific_from_json(3, fm.data_path + "/AStarRawData.json"),
        cmap="gist_gray_r",
        save=fm.images_path + '/test_texture.png'
    )

    # Create Terrain
    # max_z = fm.get_max_height()
    # min_z = fm.get_min_height()
    # terrain = Image.new("RGB", (SIZE_CONSTANT, SIZE_CONSTANT))
    # arr = get_specific_from_json(8, fm.data_path + "/AStarRawData.json")
    # print(arr)
    # abs_max_z = max_z
    #
    # for y in range(len(arr)):
    #     for x in range(len(arr[y])):
    #         print(arr[y][x])
    #         print(abs(min_z))
    #         print(abs_max_z)
    #         iterations = int((arr[y][x] + abs(min_z)) / abs_max_z) * 10
    #         print(iterations)
    #         print("======")
    #         color = get_height_color(iterations)
    #         terrain.putpixel((x, y), color)
    # terrain.save(fm.images_path + "/texture.png")


def get_height_color(iterations: int) -> tuple:
    my_color = 0
    for i in range(iterations):
        my_color += int(random.randint(0, 10) * (255 / 10)) # Gets color values for a height. z
    my_color = 255 - my_color # Converts everything to grayscale

    return my_color, my_color, my_color

# def get_height_color(iterations: int) -> tuple:
#     if iterations == 0:
#         return 0, 0, 0
#     else:
#         grayscale = int(iterations * (255 / 10))
#         inverted_grayscale = 255 - grayscale
#         return inverted_grayscale, inverted_grayscale, inverted_grayscale


def draw_path(path, image, color):
    for i in tqdm(range(len(path)), desc="Drawing A* Path"):
        image.putpixel(path[0], path[1], color)
        print(f"\rCreating Path Image. {round(i / len(path), 4)}% complete", end="")
    return image


if __name__ == "__main__":
    draw_all()

    # Image Scaling for Faster Ursina Runs
    downscaled = resize(
        image_path=fm.images_path + '/RAW_heightmap.png',
        new_name='processed_heightmap',
        scale=128
    )

    move(fm.images_path + '/processed_heightmap.png', getcwd() + '/processed_heightmap.png')

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
