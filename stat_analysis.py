import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from qgis.PyQt.QtWidgets import QGraphicsScene
from .peel_stat_results_dialog import DlgResults
from .peel_orange_functions import *


class StatAnalysis:
    def __init__(self, lyr):
        self.field_name = 'scale_dist'
        self.lyr = lyr
        self.data_list = self.get_data_list()
        self.stats_dict = self.get_stats_dict()
        self.dlg = DlgResults()

    def get_data_list(self):
        my_data_points = []
        field_index = self.lyr.fields().indexFromName(self.field_name)
        for i in self.lyr.getFeatures():
            my_data_points.append(i.attributes()[field_index])
        return my_data_points

    def get_stats_dict(self):
        return {'mean': np.mean(self.data_list),
                'std': np.std(self.data_list),
                'max': np.max(self.data_list),
                'min': np.min(self.data_list)}

    def create_plot(self, pretty_lyr_name: str):
        fig = plt.figure()
        ax = fig.add_subplot()
        plt.grid()
        # img = plt.imread(resolve_path("./img/oranges_background.jpg"))
        # ax.imshow(img, extent=[-5, 80, -5, 30])
        ax.set_title(f'{pretty_lyr_name} point scale distribution')
        ax.set_xlabel('Scale Distortion')
        ax.set_ylabel('Number of Points')
        print(plt.hist(self.data_list, bins=50, density=False, alpha=0.6, color='b'))
        # Plot the average and standard deviations
        plt.axvline(x=self.stats_dict['mean'], ls="--", color='#2ca02c', alpha=0.95)
        plt.axvline(x=(self.stats_dict['mean'] - self.stats_dict['std']), ls="--", color='#2ca02c', alpha=0.25)
        plt.axvline(x=(self.stats_dict['mean'] + self.stats_dict['std']), ls="--", color='#2ca02c', alpha=0.25)
        # TODO add threshold axvline
        # TODO add labels to axvlines (see https://stackoverflow.com/questions/13413112/creating-labels-where-line-appears-in-matplotlib-figure)
        canvas = FigureCanvas(fig)
        self.dlg.lytMain.addWidget(canvas)
        plt.close()  # Must do this or it will plot twice!

    def show_plot(self):
        self.dlg.show()
        self.dlg.exec_()
