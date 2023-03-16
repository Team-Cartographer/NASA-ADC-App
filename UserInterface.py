
import PySimpleGUI as sg
from FileManager import images_path, get_size_constant
from io import BytesIO
from PIL import Image
from numpy import array, uint8


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
            print(values["-LatIN-"], values["-LongIN-"], values["-HeightIN-"], values["-SlopeIN-"], values["-DistIN-"])
            #return values["-LatIN-"], values["-LongIN-"], values["-HeightIN-"], values["-SlopeIN-"], values["-DistIN-"]

def array_to_data(array):
    im = Image.fromarray(array)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


def get_pathfinding_endpoints():
    cur_state = 0  # 0 is no set, 1 is set start, 2 is set goal.
    # There should be an easier way to do this, but this works for now
    layout = [

        [
            sg.Graph(canvas_size=(500, 500), graph_top_right=(get_size_constant(), 0),
                     graph_bottom_left=(0, get_size_constant()), background_color="green",
                     key="-GraphIN-", enable_events=True, drag_submits=False)
        ],
        [
            sg.Text("Current Start Position:"),
            sg.Input(default_text="None", key="-StartOUT-", disabled=True),
            sg.Button("Set", key="-StartIN-")
        ],
        [
            sg.Text("Current Start Position:"),
            sg.Input(default_text="None", key="-GoalOUT-", disabled=True),
            sg.Button("Set", key="-GoalIN-")
        ],
        [
            sg.Listbox(["Heightmap", "Slopemap", "Heightkey"], default_values="Slopemap",
                       select_mode="LISTBOX_SELECT_MODE_SINGLE", enable_events=True, key="-Map-"),
            sg.OK("Submit", key="-Submit-")
        ]
    ]

    im = Image.open(images_path + "/interface_texture.png")
    arr = array(im, dtype=uint8)
    data = array_to_data(arr)

    window = sg.Window("PathFetcher", layout)
    graph = window["-GraphIN-"]
    graph.draw_image(data=data, location=(0, 500))
    window.read()

    while True:
        event, values = window.read()

        if event == "-Map-":
            map=values["-Map-"]
            if map == ['Heightmap']:
                window["-GraphIN-"].draw_image(images_path + "/interface_texture.png", location=(0, 0))
            elif map == ['Slopemap']:
                window["-GraphIN-"].draw_image(images_path + "/interface_slopemap.png", location=(0, 0))
            elif map == ['Heightkey']:
                window["-GraphIN-"].draw_image(images_path + "/interface_heightkey.png", location=(0, 0))


        if event == "-StartIN-":
            cur_state = 1

        if event == "-GoalIN-":
            cur_state = 2

        if event == "-GraphIN-":
            mouse_pos = values["-GraphIN-"]
            if cur_state == 1:
                window["-StartOUT-"].update(value=mouse_pos)
                event, values = window.read()
                print(values["-StartOUT-"])
            if cur_state == 2:
                window["-GoalOUT-"].update(value=mouse_pos)
                event, values = window.read()
                print(values["-GoalOUT-"])
            cur_state = 0


        if event == sg.WIN_CLOSED or event == "Exit":
            return None

        if event == "-Submit-":
            return values["-StartOUT-"], values["-GoalOUT-"]


if __name__ == "__main__":
    # path_fetcher()
    get_pathfinding_endpoints()
    pass
