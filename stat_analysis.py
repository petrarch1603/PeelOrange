"""Module for stat analysis classes and functions"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .peel_stat_results_dialog import DlgResults
from qgis.core import QgsVectorLayer


class StatAnalysis:
    """Class for doing stat analysis"""
    def __init__(self, lyr: QgsVectorLayer, threshold: float):
        self.field_name = 'scale_dist'
        self.lyr = lyr
        self.data_list = self.get_data_list()
        self.stats_dict = self.get_stats_dict()
        self.threshold = threshold
        self.dlg = DlgResults()

    def get_data_list(self) -> list:
        """Get data as a list"""
        my_data_points = []
        field_index = self.lyr.fields().indexFromName(self.field_name)
        for i in self.lyr.getFeatures():
            my_data_points.append(i.attributes()[field_index])
        return my_data_points

    def get_stats_dict(self) -> dict:
        """Get statistical information as dictionary"""
        return {'mean': np.mean(self.data_list),
                'std': np.std(self.data_list),
                'max': np.max(self.data_list),
                'min': np.min(self.data_list)}

    def create_plot(self, pretty_lyr_name: str) -> None:
        """Create plot"""
        fig = plt.figure()
        ax = fig.add_subplot()
        plt.grid()
        ax.set_title(f'{pretty_lyr_name} point scale distribution')
        ax.set_xlabel('Scale Distortion')
        ax.set_ylabel('Number of Points')
        # print(plt.hist(self.data_list, bins=50, density=False, alpha=0.6, color='b'))

        # Plot the average and standard deviations
        plt.axvline(x=self.stats_dict['mean'], ls="--", color='#2ca02c', alpha=0.95)
        plt.axvline(x=(self.stats_dict['mean'] - self.stats_dict['std']), ls="--", color='#2ca02c', alpha=0.25)
        plt.axvline(x=(self.stats_dict['mean'] + self.stats_dict['std']), ls="--", color='#2ca02c', alpha=0.25)
        if self.threshold != 0:
            plt.axvline(x=(1 + (self.threshold/100)), ls=":", color='#FFFF00', alpha=0.25)
            plt.axvline(x=(1 - (self.threshold/100)), ls=":", color='#FFFF00', alpha=0.25)
        #  TODO add labels to axvlines
        #   (see https://stackoverflow.com/questions/13413112/creating-labels-where-line-appears-in-matplotlib-figure)
        canvas = FigureCanvas(fig)
        self.dlg.lytMain.addWidget(canvas)
        plt.close()  # Must do this or it will plot twice!

    def show_plot(self) -> None:
        """Show the plot"""
        self.dlg.show()
        self.dlg.exec_()
