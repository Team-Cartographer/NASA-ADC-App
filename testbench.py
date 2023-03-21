from PIL import Image
import random
from utils import load_json, timeit
import os
import numpy as np
import cv2
import FileManager as fm
# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
# import numpy as np
# import FileManager as fm
#
# parsed_arr = np.array(fm.load_json(fm.data_path + "/AStarRawData.json"))
# # x[0], y[1], z[2], slope[3], azi[4], elev[5], lat[6], long[7], height[8]
#
# # Create the array of height values
# # heights = np.array([[[x, y, x**2 + y**2] for x in range(20)] for y in range(20)])
#
# # Extract the height values
# heights = parsed_arr[:, :, 8]
# #print(np.max(z))
# # Create the x and y coordinate arrays
# x, y = np.meshgrid(range(heights.shape[0]), range(heights.shape[1]))
#
# # Show height map in 3D
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot_surface(x, y, heights)
# plt.title('z as 3d height map')
# plt.show()
#
# # Show height map in 2D
# plt.figure()
# plt.title('z as 2d heat map')
# p = plt.imshow(heights)
# plt.colorbar(p)
# plt.show()

# class TerrainGenerator:
#     @timeit
#     def __init__(self, size_constant: int, arr: list[float], min_z: float, max_z: float):
#         self.size_constant = size_constant
#         arr_smoothed = np.zeros_like(arr)
#         for y in range(1, len(arr) - 1):
#             for x in range(1, len(arr[y]) - 1):
#                 arr_smoothed[y][x] = min(arr[y][x], arr[y - 1][x], arr[y][x - 1], arr[y + 1][x], arr[y][x + 1])
#
#         self.arr = arr_smoothed
#         self.min_z = min_z
#         self.max_z = max_z
#
#     @timeit
#     def generate_terrain(self) -> Image:
#         terrain = Image.new("RGB", (self.size_constant, self.size_constant))
#         abs_max_z = abs(self.min_z) + self.max_z
#
#         for y in range(len(self.arr)):
#             for x in range(len(self.arr[y])):
#
#                 iterations = int((self.arr[y][x][2] + abs(self.min_z)) / abs_max_z * 10 * random.uniform(0.9, 1.1))
#
#                 z = self.arr[y][x][2] # Get Z Val
#                 color = self.get_height_color(iterations)
#                 terrain.putpixel((x, y), color)
#
#         return terrain
#
#     # def get_height_color(self, z: float) -> tuple:
#     #     if z < self.min_z:
#     #         z = self.min_z
#     #     elif z > self.max_z:
#     #         z = self.max_z
#     #     grayscale = int((z - self.min_z) * (255 / (self.max_z - self.min_z)))
#     #     inverted_grayscale = 255 - grayscale
#     #     return inverted_grayscale, inverted_grayscale, inverted_grayscale
#
#     # def get_height_color(self, iters: int) -> tuple:
#     #     my_color = 0
#     #     contrast_multiplier = 2.5
#     #     for i in range(iters):
#     #         my_color += int(random.randint(0, 10) * (255 / 10))
#     #     my_color = int((255 - my_color) * contrast_multiplier)
#     #     if my_color < 0:
#     #         my_color = 0
#     #
#     #     return my_color, my_color, my_color
#
#     def get_height_color(self, iterations: int) -> tuple:
#         contrast_multiplier = 2.5
#         gray_range = (60, 200)  # Range of gray values to use
#         gray = random.randint(*gray_range)  # Generate a random gray value within the range
#
#         # Adjust the gray value based on the number of iterations
#         gray -= int(iterations * contrast_multiplier)
#         if gray < gray_range[0]:
#             gray = gray_range[0]
#         elif gray > gray_range[1]:
#             gray = gray_range[1]
#
#         return gray, gray, gray
#
#
# SIZE_CONSTANT = 1277
# #arr = [[random.uniform(0, 5119.0) for _ in range(SIZE_CONSTANT)] for _ in range(SIZE_CONSTANT)]
# arr = load_json(os.getcwd() + "/Data/AStarRawData.json")
# min_z = 0
# max_z = 5119.0
#
# terrain_generator = TerrainGenerator(SIZE_CONSTANT, arr, min_z, max_z)
# terrain_image = terrain_generator.generate_terrain()
# terrain_image.save("terrain.png")
