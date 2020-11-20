import json
import io
import PySimpleGUI as sg

s = {}
_sub_col = []
_width = 0
_height = 0


def write_settings():
    """
    Write settings into JSON files
    :return: None
    """
    # For each sub collection
    for col in _sub_col:
        # Update values
        for key in col[0]:
            col[0][key] = s[key]
        # Write values into file
        with io.open(col[1], 'w', encoding='utf-8-sig') as f:
            json.dump(col[0], f, indent=4)


def read_settings(filename):
    """
    Read visual settings from JSON files
    :param filename: Json visual settings file name
    :return: None
    """
    global s
    for fn in filename:
        with io.open(fn, 'r', encoding='utf-8-sig') as f:
            params = json.load(f)
            _sub_col.append((params, fn))
            s.update(params)


def init_size(size):
    """
    Initialize starting window size
    :param size: Tuple of screen size (width, height)
    :return: None
    """
    global _width, _height
    _width = size[0]
    _height = size[1]


def edit(size):
    """
    Edit settings by creating new edit window. Save on close
    :param size: Tuple of screen size (width, height)
    :return: None
    """
    # global _width, _height
    if _width != size[0] or _height != size[1]:
        s['width'] += size[0] - _width
        s['height'] += size[1] - _height
    layout = []
    for key in s:
        layout.append([sg.Text(key, size=(12, 1)), sg.Input(s[key], key=key)])
    layout.append([sg.Submit('Save'), sg.Cancel()])
    window = sg.Window('Modify settings', layout, resizable=True, auto_size_text=True, auto_size_buttons=True)
    event, values = window.read()
    if event is not None and event in 'Save':
        for key in s:
            if type(s[key]) == int:
                s[key] = int(values[key])
            elif type(s[key]) == float:
                s[key] = float(values[key])
            else:
                s[key] = values[key]
        write_settings()

    window.close()

