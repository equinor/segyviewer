import os
from unittest import TestCase
from segyviewlib import resource_icon_path, SegyTabWidget, SegyViewWidget
from PyQt4.QtGui import QApplication
from os import path

file_prefix = path.abspath(path.join(path.dirname(path.abspath(__file__)), "testdata"))

def data_path(name):
    return path.join(file_prefix, name)

app = QApplication([])

class TestSegyView(TestCase):
    def setUp(self):
        self.filename = "tests/testdata/small.sgy"

    def test_resources(self):
        icons = ['cog.png',
                 'folder.png',
                 'layouts_four_grid.png',
                 'layouts_single.png',
                 'layouts_three_bottom_grid.png',
                 'layouts_three_horizontal_grid.png',
                 'layouts_three_left_grid.png',
                 'layouts_three_right_grid.png',
                 'layouts_three_top_grid.png',
                 'layouts_three_vertical_grid.png',
                 'layouts_two_horizontal_grid.png',
                 'layouts_two_vertical_grid.png',
                 'table_export.png']

        for icon in icons:
            path = resource_icon_path(icon)
            print(path)
            self.assertTrue(os.path.exists(path))

    def test_initiate_empty_tab_widget_and_add_one(self):
        filename = "small.sgy"
        tabwidget = SegyTabWidget()

        widget = SegyViewWidget(data_path(filename))
        tabwidget.add_segy_view_widget(tabwidget.count(), widget)
