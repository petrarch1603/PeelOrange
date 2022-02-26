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


def get_cell_size(lyr, divisible=100):
    # Get shorter distance of sides of extent
    my_min = min(lyr.extents().width(), lyr.extents().height())
    return int(my_min/100)
