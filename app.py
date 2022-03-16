from .peel_orange_functions import *
from math import hypot
import processing
from qgis.core import QgsProcessing, \
    QgsCoordinateTransform, \
    QgsFeature, \
    QgsField, \
    QgsDistanceArea, \
    QgsCoordinateReferenceSystem, \
    QgsGeometry, \
    QgsPointXY, \
    QgsProject, \
    QgsVectorLayer, \
    edit

from qgis.PyQt.QtCore import QVariant


class App:
    """ Main App Class"""
    def __init__(self, lyr: QgsVectorLayer, threshold: int):
        self.lyr = lyr
        self.threshold = threshold
        self.cell_size = self.get_cell_size()  # Why did we past self.lyr here before?
        self.hex_grid = self.create_grid()
        self.centroid_lyr = self.create_centroids()
        self.scales_list = self.add_scales_to_centroid()
        self.assigned_hex_grid: QgsVectorLayer = self.assign_scales_to_grid()
        self.my_renderer = set_graduated_symbol(self.assigned_hex_grid, threshold=self.threshold)
        self.assigned_hex_grid.setRenderer(self.my_renderer)
        self.assigned_hex_grid.reload()

    def get_cell_size(self) -> int:
        """ Get Cell Size """
        # Get shorter distance of sides of extent
        my_min = min(self.lyr.extent().width(), self.lyr.extent().height())
        return int(my_min / 100)

    def create_grid(self) -> object:
        """ Creates Grid
        """
        hex_dict = {'CRS': self.lyr.crs(),
                    'EXTENT': self.lyr.extent(),
                    'HOVERLAY': 0,
                    'HSPACING': self.cell_size,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                    'TYPE': 4,  # 4 is for Hexagons
                    'VOVERLAY': 0,
                    'VSPACING': self.cell_size}
        return processing.run('native:creategrid', hex_dict)['OUTPUT']

    def create_centroids(self) -> QgsVectorLayer:
        """ Create Centroids Layer """
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

    def add_scales_to_centroid(self) -> list:
        """ Adds scales to centroid layer"""
        scale_field_idx = self.centroid_lyr.fields().indexOf('scale_dist')
        abs_field_idx = self.centroid_lyr.fields().indexOf('abs_delta')
        my_scales_list = []
        with edit(self.centroid_lyr):
            for f in self.centroid_lyr.getFeatures():
                # Get scale distortion
                my_point = PeelPointObject(point=f.geometry(),
                                           grid_crs=self.centroid_lyr.crs(),
                                           armspan=self.cell_size)
                # Add Scale Distortion
                self.centroid_lyr.changeAttributeValue(fid=f.id(),
                                                       field=scale_field_idx,
                                                       newValue=my_point.scale_distortion)
                # Add Absolute Delta
                my_abs_delta = abs(1-my_point.scale_distortion)
                self.centroid_lyr.changeAttributeValue(fid=f.id(),
                                                       field=abs_field_idx,
                                                       newValue=my_abs_delta)
                my_scales_list.append(my_point.scale_distortion)
        return my_scales_list

    def assign_scales_to_grid(self) -> QgsVectorLayer:
        """ Assign scales to grid layer """
        join_dict = {'DISCARD_NONMATCHING': True,
                     'INPUT': self.hex_grid,
                     'JOIN': self.centroid_lyr,
                     'JOIN_FIELDS': ['scale_dist', 'abs_delta'],
                     'METHOD': 1,
                     'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                     'PREDICATE': [0, 1],
                     'PREFIX': ''}
        return processing.run('native:joinattributesbylocation', join_dict)['OUTPUT']


class PeelPointObject:
    """ Calculates the scale distortion of a given point """
    def __init__(self, point: QgsFeature, grid_crs: QgsCoordinateReferenceSystem, armspan: int):
        """
        :type armspan: float, int - This is the span of distance both north/south and east/west from the point
        """
        self.point = point
        self.grid_crs = grid_crs
        self.wgs_crs = QgsCoordinateReferenceSystem.fromEpsgId(epsg=4326)
        self.armspan = 0.0003615119289149707  # This number is decimal degrees
        # This is the old way of doing it
        # self.x = self.point.asPoint().x()
        # self.y = self.point.asPoint().y()
        # self.e_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x + (self.armspan / 2), self.y))
        # self.w_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x - (self.armspan / 2), self.y))
        # self.n_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x, self.y + (self.armspan / 2)))
        # self.s_grid = QgsGeometry.fromPointXY(QgsPointXY(self.x, self.y - (self.armspan / 2)))
        self.center_wgs = self.tr(source_crs=self.grid_crs, dest_crs=self.wgs_crs, my_point=self.point)
        self.e_wgs = QgsGeometry.fromPointXY(QgsPointXY((self.center_wgs.asPoint().x() + self.armspan),
                                                        self.center_wgs.asPoint().y()))
        self.w_wgs = QgsGeometry.fromPointXY(QgsPointXY((self.center_wgs.asPoint().x() - self.armspan),
                                                        self.center_wgs.asPoint().y()))
        self.n_wgs = QgsGeometry.fromPointXY(QgsPointXY(self.center_wgs.asPoint().x(),
                                                        (self.center_wgs.asPoint().y() + self.armspan)))
        self.s_wgs = QgsGeometry.fromPointXY(QgsPointXY(self.center_wgs.asPoint().x(),
                                                        (self.center_wgs.asPoint().y() - self.armspan)))
        self.e_grid = self.tr(source_crs=self.wgs_crs, dest_crs=self.grid_crs, my_point=self.e_wgs)
        self.w_grid = self.tr(source_crs=self.wgs_crs, dest_crs=self.grid_crs, my_point=self.w_wgs)
        self.n_grid = self.tr(source_crs=self.wgs_crs, dest_crs=self.grid_crs, my_point=self.n_wgs)
        self.s_grid = self.tr(source_crs=self.wgs_crs, dest_crs=self.grid_crs, my_point=self.s_wgs)
        self.e_w_wgs_dist = self.wgs_dist(self.e_wgs, self.w_wgs)
        self.n_s_wgs_dist = self.wgs_dist(self.n_wgs, self.s_wgs)
        # self.avg_dist = (self.e_w_dist + self.n_s_dist) / 2
        self.n_s_grid_dist = self.pythag_dist(grid_point1=self.n_grid, grid_point2=self.s_grid)
        self.e_w_grid_dist = self.pythag_dist(grid_point1=self.e_grid, grid_point2=self.w_grid)
        self.h = self.n_s_grid_dist / self.n_s_wgs_dist
        self.k = self.e_w_grid_dist / self.e_w_wgs_dist
        self.scale_distortion = self.determine_greatest_delta()

    def tr(self,
           source_crs: QgsCoordinateReferenceSystem,
           dest_crs: QgsCoordinateReferenceSystem,
           my_point: QgsGeometry) -> QgsGeometry:
        """ transform from source to destination """
        my_tr = QgsCoordinateTransform(source_crs,
                                       dest_crs,
                                       QgsProject.instance())
        new_point = QgsGeometry(my_point)
        new_point.transform(my_tr)
        return new_point

    def determine_greatest_delta(self) -> float:
        """
        Determine which distance departs from the armspan the most. This number is the
        greatest scale distortion for a given point.
        """
        if abs(1-self.h) > abs(1-self.k):
            return self.h
        else:
            return self.k

    def wgs_dist(self, wgs_point1, wgs_point2):
        """ Get Distance using Vincent's formula """
        da = QgsDistanceArea()
        da.setSourceCrs(self.wgs_crs, QgsProject.instance().transformContext())
        da.setEllipsoid("WGS84")
        return da.measureLine(wgs_point1.asPoint(), wgs_point2.asPoint())

    def pythag_dist(self, grid_point1, grid_point2):
        """ Get Grid Distance using Pythagorean Theorem """
        x_side = abs(grid_point1.asPoint().x() - grid_point2.asPoint().x())
        y_side = abs(grid_point1.asPoint().y() - grid_point2.asPoint().y())
        return hypot(x_side, y_side)
