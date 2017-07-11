import os
from unittest import TestCase
from segyviewlib import resource_icon_path


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
