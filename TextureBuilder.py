import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise


def generate_noisemap():
    noise = PerlinNoise(octaves=5, seed=50)
    xpix, ypix = 100, 100
    pic = [[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)]

    plt.imshow(pic, cmap='gray')
    plt.show()


if __name__ == "__main__":
    generate_noisemap()