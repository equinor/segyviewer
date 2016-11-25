import os
from unittest import TestCase
from segyviewlib import resource_icon_path


class TestSegyView(TestCase):
    def setUp(self):
        self.filename = "test-data/small.sgy"

    def test_resources(self):
        path = resource_icon_path("layouts_single.png")
        print(path)
        self.assertTrue(os.path.exists(path))

