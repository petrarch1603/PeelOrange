# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PeelOrange
                                 A QGIS plugin
 This plugin visualizes the scale distortion for a given region
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-02-20
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Patrick McGranaghan
        email                : ptmcgra@yahoo.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import importlib
import pyproj
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QGraphicsScene
from qgis.core import QgsMapLayerProxyModel



# Initialize Qt resources from file resources.py
# from .resources import *
# Import the code for the dialog
from .peel_orange_dialog import PeelOrangeDialog
import os.path
# from .peel_orange_functions import *
from .app import *
from .stat_analysis import *
from .peel_stat_results_dialog import DlgResults
from qgis.core import QgsMessageLog, Qgis, QgsProject


class PeelOrange:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PeelOrange_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Peel Orange Scale Distortion Visualizer')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.do_stat_analysis_flag = False
        self.do_thresh_flag = False

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PeelOrange', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(resolve_path(icon_path))
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/peel_orange/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PeelOrange - Scale Distortion Visualizer'),
            callback=self.run,
            parent=self.iface.mainWindow())
        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Peel Orange Scale Distortion Visualizer'),
                action)
            self.iface.removeToolBarIcon(action)

    # noinspection PyTypeChecker,PyCallByClass
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            # Check that the CRS is a projected coordinate system
            if QgsProject.instance().crs().mapUnits() == 6:
                print(QgsProject.instance().crs().mapUnits())
                # QgsProject.messageBar().pushMessage("bad crs!")
                warn_box = QMessageBox()
                warn_box.setIcon(QMessageBox.Information)
                warn_box.setText("Warning: project is using a geographic coordinate system.\n"
                                 "Peel Orange only works on projected coordinate systems")
                warn_box.exec_()
                return
            self.first_start = False
            self.dlg = PeelOrangeDialog()
            self.dlg.warn_label.setText('')
            # Ensure that CRS is a projected coordinate system
            # if QgsProject.instance().crs().mapUnits():
            #     self.dlg.button_box.setDisabled(True)
            # Set up and filter the layer combo box
            layers_list = list(QgsProject.instance().mapLayers().values())  # This could probably be more elegant
            # excluded_list = exclude_layers_from_box(layers=layers_list, project_crs=QgsProject.instance().crs())

            # Set so Map Layer Combo Box Defaults to blank
            self.dlg.mLCB.setCurrentIndex(-1)

            # self.dlg.mLCB.setExceptedLayerList(excluded_list)
            self.dlg.mLCB.setShowCrs(True)
            self.dlg.mLCB.setFilters(QgsMapLayerProxyModel.HasGeometry)
            print(self.dlg.mLCB)
            self.dlg.mLCB.layerChanged.connect(self.mlcb_layerChanged)

            self.dlg.stat_analysis_checkBox.stateChanged.connect(self.stat_analysis_checkBox_changed)

            # Set up threshold
            self.dlg.thresholdBox.setDisabled(True)
            self.dlg.thresh_checkBox.setToolTip('Threshold is the amount of scale distortion tolerance to '
                                                'visualize in the drawing')
            self.dlg.thresh_checkBox.stateChanged.connect(self.thresh_checkBox_changed)

            # Get Metadata as a dictionary
            meta_dict = read_metadata_txt('metadata.txt')
            version_no = meta_dict['version']
            self.dlg.version_label.setStyleSheet('color: light-gray')
            self.dlg.version_label.setText(f"Version {version_no}")
            self.dlg.warn_label.setStyleSheet('color: red')

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Store user selections as variables.
            my_lyr: object = self.dlg.mLCB.currentLayer()
            if self.do_thresh_flag is True:
                threshold = float(float(self.dlg.thresholdBox.cleanText())/100)
            else:
                threshold = 0

            # Add a log message
            post_log_message("Analysis beginning")

            # Run app
            my_app = App(my_lyr, threshold)
            QgsProject.instance().addMapLayer(my_app.assigned_hex_grid, True)  # You can use false here to hide it
            # TODO add option and handling for centroid points
            # QgsProject.instance().addMapLayer(my_app.centroid_lyr, True)  # You can use false here to hide it

            # Statistical Analysis Process
            if self.do_stat_analysis_flag:
                stat_analysis = StatAnalysis(lyr=my_app.assigned_hex_grid, threshold=threshold)
                my_dict = stat_analysis.get_stats_dict()
                my_log = ""
                for k, v in my_dict.items():
                    my_log += f"{k}: {v}\n"
                post_log_message(my_log)
                add_metadata_to_layer(lyr=my_app.assigned_hex_grid, meta_str=my_log)

                # Show the results dialog
                stat_analysis.create_plot(f"{my_lyr.name()}")
                stat_analysis.show_plot()

    def mlcb_layerChanged(self, lyr):
        if lyr is None:
            return
        self.dlg.mLCB.setLayer(lyr)
        if self.dlg.mLCB.currentLayer().featureCount() == 0:
            self.dlg.warn_label.setText('Selected Layer Has No Features')
            self.dlg.exec_button.setEnabled(False)
        elif self.dlg.mLCB.currentLayer().geometryType() == 0 and self.dlg.mLCB.currentLayer().featureCount() < 2:
            self.dlg.warn_label.setText('Selected Layer is a Point Layer and does not have enough features')
            self.dlg.exec_button.setEnabled(False)
        elif self.dlg.mLCB.currentLayer().crs() != QgsProject.instance().crs():
            self.dlg.warn_label.setText('Selected Layer is not on the same CRS as the project.')
            self.dlg.exec_button.setEnabled(False)
        else:
            self.dlg.warn_label.setText('')
            self.dlg.exec_button.setEnabled(True)

    def stat_analysis_checkBox_changed(self, state):
        if state == Qt.Checked:
            self.do_stat_analysis_flag = True
            stat_pix = QPixmap(resolve_path("img/stat_img_clean.png"))
            self.dlg.stat_analysis_img.setPixmap(stat_pix)
        else:
            self.do_stat_analysis_flag = False
            stat_pix = QPixmap(resolve_path("img/stat_img_blur.png"))
            self.dlg.stat_analysis_img.setPixmap(stat_pix)

    def thresh_checkBox_changed(self, state):
        if state == Qt.Checked:
            self.do_thresh_flag = True
            self.dlg.thresholdBox.setDisabled(False)
            thresh_pix = QPixmap(resolve_path("img/w-thresh.png"))
            self.dlg.threshold_img.setPixmap(thresh_pix)
            print(f"Is the pic null? {thresh_pix.isNull()}")
        else:
            self.do_thresh_flag = False
            self.dlg.thresholdBox.setDisabled(True)
            thresh_pix = QPixmap(resolve_path("img/no-thresh.png"))
            self.dlg.threshold_img.setPixmap(thresh_pix)
            print('change no-thresh')
