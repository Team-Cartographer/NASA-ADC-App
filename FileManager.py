"""
FileManager.py makes folders and directories for all files for the FPA Team NASA
App Development Challenge Application.#
"""

import os
from shutil import move
from dotenv import load_dotenv, set_key
from utils import show_error, show_info
from csv import reader
import json
from time import localtime, strftime

class Save:
    def __init__(self, json_path, folder_path):
        self.json_path = json_path
        self.folder_path = folder_path
        print(f'Saved')

# Setting up '.env' created by PathFetcher
if not os.path.exists(os.getcwd() + '/.env'):

    # Checks for existence of '.env' before setup
    if not os.path.exists(os.getcwd() + '/PathFetcher/.env'):
        show_error("Failure", 'Please run PathFetcher.exe first.')
        quit()

    dotenv_path = (os.getcwd() + "/PathFetcher/.env").replace("\\", "/")
    # Fixes Pathing
    dotenv_path = move(dotenv_path, os.getcwd())

load_dotenv()


# Getter Functions for '.env'
def get_latitude_file_path() -> str:
    return os.getenv('LATITUDE_FILE_PATH').replace("\\", "/")


def get_longitude_file_path() -> str:
    return os.getenv('LONGITUDE_FILE_PATH').replace("\\", "/")


def get_height_file_path() -> str:
    return os.getenv('HEIGHT_FILE_PATH').replace("\\", "/")


def get_slope_file_path() -> str:
    return os.getenv('SLOPE_FILE_PATH').replace("\\", "/")


def get_dist_between_points() -> int:
    return int(os.getenv('DISTANCE_BETWEEN_POINTS'))


def get_size_constant() -> int:
    return int(os.getenv("SIZE_CONSTANT"))


def get_max_z() -> int:
    return int(os.getenv("MAX_Z"))


def get_min_z() -> int:
    return int(os.getenv('MIN_Z'))


def get_min_x() -> int:
    return int(os.getenv('MIN_X'))


def get_min_y() -> int:
    return int(os.getenv('MIN_Y'))


def get_lunar_rad() -> float:
    return float(os.getenv('LUNAR_RAD'))

'''
def load_save(json_path : str) -> dict:
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def write_save(latitude_path : str, longitude_path : str,
               height_path : str, slope_path : str, dist : str,
               size_constant : str , player_pos : str) -> str:
    data : dict = {
        "LATITUDE_PATH": latitude_path,
        "LONGITUDE_PATH": longitude_path,
        "HEIGHT_PATH": height_path,
        "SLOPE_PATH": slope_path,

        "DIST_BETWEEN_POINTS": dist,
        "SIZE_CONSTANT": size_constant,
        "PLAYER_POSITION": player_pos
    }

    date : str = str(strftime("%Y-%m-%d %H:%M:%S", localtime())).replace(":", "-")
    jsonpath : str = os.path.join(os.getcwd(), f'{date}.json')
    with open(jsonpath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonpath
'''


# IMPORTANT PATHING
parent_path: str = os.getcwd()
data_path: str = os.path.join(parent_path, 'Data')
images_path: str = os.path.join(data_path, 'Images')
app_files_path: str = os.path.join(parent_path, 'App Files')
archive_path: str = os.path.join(app_files_path, 'Archived Files')

# Creates directories and sets '.env' variables only if FileManager.py is running.
# Otherwise, only helper methods are accessible.
if __name__ == '__main__':
    with open(get_slope_file_path()) as f:
        size_cons = len(list(reader(f)))
    set_key('.env', 'SIZE_CONSTANT', str(size_cons))
    set_key('.env', 'LUNAR_RAD', str(1737.4 * 1000))
    if not os.path.exists(os.path.join(parent_path, 'Data')):
        os.mkdir(data_path)
        os.mkdir(app_files_path)
        os.mkdir(archive_path)
        os.mkdir(images_path)
    else:
        # If Directories exist, Notify User.
        show_info('ADC App Installation Update',
                  "Folder Already Exists on " + parent_path + '\nFiles have been updated.')


