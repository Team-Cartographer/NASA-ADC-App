"""
FileManager.py makes folders and directories for all files for the FPA Team NASA
App Development Challenge Application.#
"""

import os
from utils import show_info
from csv import reader
import json
import PySimpleGUI as sg

JSONPATH = os.getcwd() + '/info.json'

# Needed here from UserInterface to avoid Circular Import
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

# Converts a CSV File to an Array, taken from Utils to avoid Circular Import
def file2list(path):
    with open(path) as csv_file:
        new_list = list(reader(csv_file, delimiter=','))
        csv_file.close()

    return new_list

# Load data from Json File
def load_json(json_path : str) -> dict:
    with open(json_path, 'r') as f:
        jsondata = json.load(f)
    return jsondata

# Push Dictionary of Data to Json File
def push_to_json(jsonpath, data):
    with open(jsonpath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Currently Disabled as Saves are not a priority task.
''' 
class Save:
    def __init__(self, name):
        latpath, longpath, heightpath, slopepath, dist_between_points = path_fetcher()
        self.json_path, self.folder_path, self.data = self.write_json(
            latitude_path=latpath, longitude_path=longpath,
            height_path=heightpath, slope_path=slopepath, dist=int(dist_between_points),
            size_constant=len(file2list(latpath)), player_pos=None, name=name)

        show_info("Save Success!",f'Saved {self.json_path}')

    #def save(self):
    
    def write_json(self, latitude_path : str, longitude_path : str,
               height_path : str, slope_path : str, dist : str,
               size_constant : str , player_pos : str, name : str):

    if not name:
        name = 0

    folder_path = os.getcwd() + f"/Save{name}"
    if not os.path.exists(folder_path):
        os.mkdir(os.getcwd() + f"/Save{name}")

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
'''


# Sets up Json File.
if not os.path.exists(os.getcwd() + '/info.json'):

    LUNAR_RAD = 1737400.0

    # Get pathing from Path_Fetcher()
    lat, long, ht, slope, dist = None, None, None, None, None
    while not lat:
        lat, long, ht, slope , dist = path_fetcher()

    data: dict = {
        "LATITUDE_PATH": lat,
        "LONGITUDE_PATH": long,
        "HEIGHT_PATH": ht,
        "SLOPE_PATH": slope,

        "DIST_BETWEEN_POINTS": int(dist),
        "SIZE_CONSTANT": len(file2list(lat)),
        "PLAYER_POSITION": None,
        "LUNAR_RAD": LUNAR_RAD,
        "MAX_Z": None,
        "MIN_Z": None,
        "MIN_Y": None,
        "MIN_X": None
    }

    push_to_json(JSONPATH, data)


# Data is a dictionary load that is standardized for all saves.
data = load_json(os.getcwd() + '/info.json')


# Getter Functions for '.json'
def get_latitude_file_path() -> str:
    return data["LATITUDE_PATH"].replace("\\", "/")


def get_longitude_file_path() -> str:
    return data["LONGITUDE_PATH"].replace("\\", "/")


def get_height_file_path() -> str:
    return data["HEIGHT_PATH"].replace("\\", "/")


def get_slope_file_path() -> str:
    return data["SLOPE_PATH"].replace("\\", "/")


def get_dist_between_points() -> int:
    return data["DIST_BETWEEN_POINTS"]


def get_size_constant() -> int:
    return data["SIZE_CONSTANT"]


def get_max_z() -> int:
    return data["MAX_Z"]


def get_min_z() -> int:
    return data["MIN_Z"]


def get_min_x() -> int:
    return data["MIN_X"]


def get_min_y() -> int:
    return data["MIN_Y"]


def get_lunar_rad() -> float:
    return data["LUNAR_RAD"]


# Meant for future save files, unused currently.
def get_player_pos() -> tuple:
    return data["PLAYER_POSITION"]


# IMPORTANT PATHING
parent_path: str = os.getcwd()
data_path: str = os.path.join(parent_path, 'Data')
images_path: str = os.path.join(data_path, 'Images')
app_files_path: str = os.path.join(parent_path, 'App Files')

# Creates directories and sets 'info.json' variables only if FileManager.py is running.
# Otherwise, only helper methods are accessible.
if __name__ == '__main__':

    # Save File proof of concept, disregard currently.
    #savetest = Save('SAVETEST')


    # json is automatically created and/or overwritten on every run of FileManager.

    if not os.path.exists(os.path.join(parent_path, 'Data')):
        os.mkdir(data_path)
        os.mkdir(app_files_path)
        os.mkdir(images_path)
    else:
        # If Directories exist, Notify User.
        show_info('ADC App Installation Update',
                  "Folder Already Exists on " + parent_path + '\nFiles have been updated.')


