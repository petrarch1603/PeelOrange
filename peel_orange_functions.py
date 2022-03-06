import os
import configparser


def get_file_path(filename: str) -> str:
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        filename))


def read_metadata_txt(filename: str) -> dict:
    metadata = []
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(get_file_path(filename))
    metadata.extend(parser.items('general'))
    return dict(metadata)


def exclude_degrees_layers(layers: list) -> list:
    excluded_list = []
    for l in layers:
        if l.crs().mapUnits() == 6:  # 6 is the unit type for degrees
            excluded_list.append(l)
    return excluded_list
