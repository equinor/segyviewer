#!/usr/bin/env python
import sys

import matplotlib.cm as mcm
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QLabel, QVBoxLayout

from segyviewlib import LayoutCombo, ColormapCombo, LayoutCanvas


class TestGUI(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("GUI Test")

        toolbar = self.addToolBar("Stuff")
        """:type: QToolBar"""

        layout_combo = LayoutCombo()
        toolbar.addWidget(layout_combo)
        layout_combo.layout_changed.connect(self._layout_changed)

        self._colormap_combo = ColormapCombo()
        toolbar.addWidget(self._colormap_combo)
        self._colormap_combo.currentIndexChanged[int].connect(self._colormap_changed)

        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self._layout_canvas = LayoutCanvas(width=5, height=5)
        self._layout_canvas.set_plot_layout(layout_combo.get_current_layout())
        layout.addWidget(self._layout_canvas)

        colormap_name = str(self._colormap_combo.itemText(0))
        self._colormap = mcm.ScalarMappable(cmap=colormap_name)
        self._colormap.set_array([])

        self._colormap_label = QLabel()
        layout.addWidget(self._colormap_label)

        self.setCentralWidget(central_widget)

        self._update_axes()

    def _update_axes(self):
        layout_figure = self._layout_canvas.layout_figure()
        colormap_axes = layout_figure.colormap_axes()
        self._colorbar = layout_figure.colorbar(self._colormap, cax=colormap_axes, use_gridspec=True)
        self._colormap_changed(self._colormap_combo.currentIndex())

    def _layout_changed(self, layout):
        self._layout_canvas.set_plot_layout(layout)
        self._update_axes()

    def _colormap_changed(self, index):
        colormap_name = str(self._colormap_combo.itemText(index))
        self._colormap.set_cmap(colormap_name)
        self._colormap_label.setText("Colormap selected: %s" % colormap_name)
        self._layout_canvas.draw()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit()
    else:
        q_app = QApplication(sys.argv)

        gui = TestGUI()
        gui.show()
        gui.raise_()
        sys.exit(q_app.exec_())
