from qgis.PyQt.QtWidgets import *


class DlgResults(QDialog, Ui_dlgResults):
    def __init__(self):
        super(DlgResults, self).__init__()
        self.setupUi(self)
