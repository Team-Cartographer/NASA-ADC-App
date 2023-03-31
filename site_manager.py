
class Site:
    def __init__(self, folder_path, site_name):
        self.folder_path = folder_path
        self.site_name = site_name
        self.data_folder = folder_path + "/Data"
        self.images_folder = folder_path + "/Images"
        self.astar_path_image = self.images_folder + "/AStar_Path.png"
        self.heightkey_surface_image = self.images_folder + "/heightkey_surface.png"
        self.interface_heightkey_image = self.images_folder + "/interface_heightkey_image.png"
        self.interface_slopemap_image = self.images_folder + "/interface_slopemap.png"
        self.interface_texture_image = self.images_folder + "/interface_texture.png"
        self.minimap_image = self.images_folder + "/minimap.png"
        self.moon_surface_texture_image = self.images_folder + "/moon_surface_texture.png"
        self.raw_heightmap_image = self.images_folder + "/RAW_heightmap.png"
        self.slopemap_image = self.images_folder + "/slopemap.png"
        self.processed_heightmap = self.images_folder + "/processed_heightmap.png"
        self.astar_json = self.data_folder + "/AStarRawData.json"


if __name__ == '__main__':
    pass
