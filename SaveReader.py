import json
from time import localtime, strftime
from os import getcwd, path


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
    jsonpath : str = path.join(getcwd(), f'{date}.json')
    with open(jsonpath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return path


