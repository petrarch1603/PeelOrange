from qgis.PyQt.QtWidgets import *
from .peel_stat_results_dialog_ui import Ui_dlgResults
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class DlgResults(QDialog, Ui_dlgResults):
    def __init__(self):
        super(DlgResults, self).__init__()
        self.setupUi(self)
        self.setLayout(self.lytMain)