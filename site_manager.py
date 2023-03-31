import ui
import os
from utils import file2list, push_to_json, load_json
from data_processor import process_data
from cartographer import create_images
from a_star import run_astar


class Save:
    def __init__(self, folder_path: str, site_name: str):
        self.folder_path = folder_path + "/Save_" + site_name
        self.site_name = site_name
        self.data_folder = self.folder_path + "/Data"
        self.images_folder = self.folder_path + "/Images"
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
        self.info_json = self.data_folder + "/Info.json"
        self.size = None
        self.latitude_path, self.longitude_path, self.height_path, self.slope_path = None, None, None, None


    def set_up(self):
        os.makedirs(self.folder_path, exist_ok=True)
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.images_folder, exist_ok=True)

        if not os.path.exists(self.info_json):
            lat, long, ht, slope = ui.path_fetcher()
            data: dict = {
                "LATITUDE_PATH": lat,
                "LONGITUDE_PATH": long,
                "HEIGHT_PATH": ht,
                "SLOPE_PATH": slope,

                "SIZE_CONSTANT": len(file2list(lat)),
            }

            push_to_json(self.info_json, data)

        data = load_json(self.info_json)

        self.latitude_path, self.longitude_path, self.height_path, self.slope_path = \
            data["LATITUDE_PATH"], data["LONGITUDE_PATH"], data["HEIGHT_PATH"], data["SLOPE_PATH"]
        self.size = data["SIZE_CONSTANT"]


        process_data(self)
        create_images(self)
        run_astar(self)


    def to_string(self):
        return f"{self.folder_path}"



def check_save():
    save_folder = os.getcwd() + '/Saves'
    os.makedirs(save_folder, exist_ok=True)

    path = ui.on_start()
    save = None

    if path:
        save = Save(path, "test")
    else:
        save = Save(save_folder, "TEMP")
        save.set_up()

    return save




