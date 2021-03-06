# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ptmcgra@yahoo.com'
__date__ = '2022-02-20'
__copyright__ = 'Copyright 2022, Patrick McGranaghan'

import unittest

from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog

from peel_orange.peel_orange_dialog import PeelOrangeDialog

from peel_orange.test.utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class PeelOrangeDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = PeelOrangeDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.exec_button.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.exec_button.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

def run_test():
    suite = unittest.makeSuite(PeelOrangeDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    print('finish')
run_test()
