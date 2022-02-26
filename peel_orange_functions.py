import os
import processing
from qgis.core import QgsProcessing, QgsVectorLayer
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
    my_min = min(lyr.extent().width(), lyr.extent().height())
    print(my_min)
    return int(my_min/100)


def create_grid(lyr):
    my_cell_size = get_cell_size(lyr)
    print(my_cell_size)
    hex_dict = {'CRS': lyr.crs(),
                'EXTENT': lyr.extent(),
                'HOVERLAY': 0,
                'HSPACING': my_cell_size,
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                'TYPE': 4,  # 4 is for Hexagons
                'VOVERLAY': 0,
                'VSPACING': my_cell_size}
    return processing.run('native:creategrid', hex_dict)['OUTPUT']


def create_centroids(lyr):
    centroid_dict = {'ALL_PARTS': True,
                     'INPUT': lyr,
                     'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
    return processing.run('native:centroids', centroid_dict)['OUTPUT']


