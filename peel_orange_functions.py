import os
import processing
from qgis.core import QgsProcessing, \
    QgsCoordinateTransform, \
    QgsField, \
    QgsDistanceArea, \
    QgsCoordinateReferenceSystem, \
    QgsGeometry, \
    QgsPointXY, \
    QgsProject, \
    edit

from qgis.PyQt.QtCore import QVariant
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


class App:
    def __init__(self, lyr, threshold):
        self.lyr = lyr
        self.threshold = threshold
        self.cell_size = self.get_cell_size(self.lyr)
        self.hex_grid = self.create_grid()
        self.centroid_lyr = self.create_centroids()
        self.scales_list = self.add_scales_to_centroid()
        self.assigned_hex_grid = self.assign_scales_to_grid()

    def get_cell_size(self, lyr, divisible=100):
        # Get shorter distance of sides of extent
        my_min = min(lyr.extent().width(), lyr.extent().height())
        return int(my_min / 100)

    def create_grid(self):
        hex_dict = {'CRS': self.lyr.crs(),
                    'EXTENT': self.lyr.extent(),
                    'HOVERLAY': 0,
                    'HSPACING': self.cell_size,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                    'TYPE': 4,  # 4 is for Hexagons
                    'VOVERLAY': 0,
                    'VSPACING': self.cell_size}
        return processing.run('native:creategrid', hex_dict)['OUTPUT']

    def create_centroids(self):
        centroid_dict = {'ALL_PARTS': True,
                         'INPUT': self.hex_grid,
                         'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
        centroid_lyr = processing.run('native:centroids', centroid_dict)['OUTPUT']
        myScaleField = QgsField('scale_dist', QVariant.Double)
        myAbsField = QgsField('abs_delta', QVariant.Double)
        centroid_lyr.dataProvider().addAttributes([myScaleField])
        centroid_lyr.dataProvider().addAttributes([myAbsField])
        centroid_lyr.updateFields()
        return centroid_lyr

    def add_scales_to_centroid(self):
        scale_field_idx = self.centroid_lyr.fields().indexOf('scale_dist')
        abs_field_idx = self.centroid_lyr.fields().indexOf('abs_delta')
        my_scales_list = []
        with edit(self.centroid_lyr):
            for f in self.centroid_lyr.getFeatures():
                my_point = MyPointObject(f.geometry(), self.centroid_lyr.crs(), self.cell_size)
                self.centroid_lyr.changeAttributeValue(f.id(), scale_field_idx, my_point.scale_distortion)
                my_abs_delta = abs(1-my_point.scale_distortion)
                self.centroid_lyr.changeAttributeValue(f.id(), abs_field_idx, my_abs_delta)
                my_scales_list.append(my_point.scale_distortion)
        return my_scales_list

    def assign_scales_to_grid(self):
        join_dict = {'DISCARD_NONMATCHING': True,
             'INPUT': self.hex_grid,
             'JOIN': self.centroid_lyr,
             'JOIN_FIELDS': ['scale_dist', 'abs_delta'],
             'METHOD': 1,
             'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
             'PREDICATE': [0, 1],
             'PREFIX': ''}
        return processing.run('native:joinattributesbylocation', join_dict)['OUTPUT']


# noinspection PyCallByClass,PyArgumentList
class MyPointObject:
    def __init__(self, point, crs, armspan):
        """
        :type armspan: float, int - This is the span of distance both north/south and east/west from the point
        """
        self.point = point
        self.crs = crs
        self.armspan = int(armspan)
        self.x = self.point.asPoint().x()
        self.y = self.point.asPoint().y()
        self.e_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x + (self.armspan / 2), self.y))
        self.w_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x - (self.armspan / 2), self.y))
        self.n_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x, self.y + (self.armspan / 2)))
        self.s_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x, self.y - (self.armspan / 2)))
        try:
            assert int(self.e_grid.asPoint().x()) - int(self.w_grid.asPoint().x()) == int(armspan)
            assert int(self.n_grid.asPoint().y()) - int(self.s_grid.asPoint().y()) == int(armspan)
        except AssertionError as e:
            print(self.e_grid.asPoint().x() - self.w_grid.asPoint().x())
            print(self.n_grid.asPoint().y() - self.s_grid.asPoint().y())
            print(e)
        self.e_wgs = self.tr(self.e_grid)
        self.w_wgs = self.tr(self.w_grid)
        self.n_wgs = self.tr(self.n_grid)
        self.s_wgs = self.tr(self.s_grid)
        self.e_w_dist = self.wgs_dist(self.e_wgs, self.w_wgs)
        self.n_s_dist = self.wgs_dist(self.n_wgs, self.s_wgs)
        self.avg_dist = (self.e_w_dist + self.n_s_dist) / 2
        self.scale_distortion = self.armspan / self.avg_dist

    def tr(self, grid_point):
        my_tr = QgsCoordinateTransform(self.crs,
                                       QgsCoordinateReferenceSystem.fromEpsgId(epsg=4326),
                                       QgsProject.instance())
        wgs_point = QgsGeometry(grid_point)
        wgs_point.transform(my_tr)
        return wgs_point

    # noinspection PyCallByClass
    def wgs_dist(self, wgs_point1, wgs_point2):
        da = QgsDistanceArea()
        da.setSourceCrs(QgsCoordinateReferenceSystem.fromEpsgId(epsg=4326), QgsProject.instance().transformContext())
        da.setEllipsoid("WGS84")
        return da.measureLine(wgs_point1.asPoint(), wgs_point2.asPoint())
