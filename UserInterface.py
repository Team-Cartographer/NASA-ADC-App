
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
            print(values["-LatIN-"], values["-LongIN-"], values["-HeightIN-"], values["-SlopeIN-"], values["-DistIN-"])
            #return values["-LatIN-"], values["-LongIN-"], values["-HeightIN-"], values["-SlopeIN-"], values["-DistIN-"]


if __name__ == "__main__":
    #path_fetcher()
    pass
