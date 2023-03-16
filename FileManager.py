"""
FileManager.py makes folders and directories for all files for the FPA Team NASA
App Development Challenge Application.#
"""

import os
from utils import show_error, show_info, show_warning
#from UserInterface import path_fetcher
from dotenv import load_dotenv, set_key
from shutil import move
from csv import reader
import json
import PySimpleGUI as sg

def path_fetcher():
    layout = [
        [
            sg.FileBrowse("Upload Latitude File", size=(20, 1), key="-LatIN-", file_types=(("CSV file", "*.csv"),)),
            sg.Input(size=(100, 1), disabled=True)
        ], [
            sg.FileBrowse("Upload Longitude File", size=(20, 1), key="-LongIN-", file_types=(("CSV file", "*.csv"),)),
            sg.Input(size=(100, 1), disabled=True)
        ], [
            sg.FileBrowse("Upload Height File", size=(20, 1), key="-HeightIN-", file_types=(("CSV file", "*.csv"),)),
            sg.Input(size=(100, 1), disabled=True)
        ], [
            sg.FileBrowse("Upload Slope File", size=(20, 1), key="-SlopeIN-", file_types=(("CSV file", "*.csv"),)),
            sg.Input(size=(100, 1), disabled=True)
        ], [
            sg.Text("Enter Distance Between Points (in meters)")
        ], [
            sg.InputText(size=(20, 1), key="-DistIN-", enable_events=True),
            sg.OK("Submit")
        ]
    ]

    window = sg.Window("PathFetcher", layout)
    while True:
        event, values = window.read()

        if event == '-DistIN-' and values['-DistIN-'] and values['-DistIN-'][-1] not in "0123456789.":
            window['-DistIN-'].update(values['-DistIN-'][:-1])
        elif len(values['-DistIN-']) > 5:
            window['-DistIN-'].update(values['-DistIN-'][:-1])

        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "Submit":
            # Latitude, Longitude, Height, Slope, Dist_Between_Points
            #print(values["-LatIN-"], values["-LongIN-"], values["-HeightIN-"], values["-SlopeIN-"], values["-DistIN-"])
            return values["-LatIN-"], values["-LongIN-"], values["-HeightIN-"], values["-SlopeIN-"], values["-DistIN-"]

    return None

def file2list(path):
    with open(path) as csv_file:
        new_list = list(reader(csv_file, delimiter=','))
        csv_file.close()

    return new_list

class Save:
    def __init__(self, name):
        latpath, longpath, heightpath, slopepath, dist_between_points = path_fetcher()
        self.json_path, self.folder_path, self.data = write_json(
            latitude_path=latpath, longitude_path=longpath,
            height_path=heightpath, slope_path=slopepath, dist=dist_between_points,
            size_constant=len(file2list(latpath)), player_pos=None, name=name)

        print(f'Saved {self.json_path}')

    #def save(self):


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


def load_json(json_path : str) -> dict:
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def write_json(latitude_path : str, longitude_path : str,
               height_path : str, slope_path : str, dist : str,
               size_constant : str , player_pos : str, name : str):

    if not name:
        name = 0

    folder_path = os.getcwd() + f"/Save{name}"
    if not os.path.exists(folder_path):
        os.mkdir(os.getcwd() + f"/Save{name}")
    else:
        show_warning("Save Error", f"Save with Name: '{name}' Exists.")
        pass

    data : dict = {
        "LATITUDE_PATH": latitude_path,
        "LONGITUDE_PATH": longitude_path,
        "HEIGHT_PATH": height_path,
        "SLOPE_PATH": slope_path,

        "DIST_BETWEEN_POINTS": dist,
        "SIZE_CONSTANT": size_constant,
        "PLAYER_POSITION": player_pos
    }

    name : str = f"Save{name}" # Hardcoded to 0 for Testing.
    jsonpath : str = os.path.join(folder_path, f'{name}.json')
    with open(jsonpath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonpath, folder_path, data



# IMPORTANT PATHING
parent_path: str = os.getcwd()
data_path: str = os.path.join(parent_path, 'Data')
images_path: str = os.path.join(data_path, 'Images')
app_files_path: str = os.path.join(parent_path, 'App Files')
archive_path: str = os.path.join(app_files_path, 'Archived Files')

# Creates directories and sets '.env' variables only if FileManager.py is running.
# Otherwise, only helper methods are accessible.
if __name__ == '__main__':

    # Testing Saves
    #savetest = Save('SAVETEST')

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


