import os
import configparser


def get_file_path(filename):
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        filename))


def read_metadata_txt(filename):
    metadata = []
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(get_file_path(filename))
    metadata.extend(parser.items('general'))
    return dict(metadata)
