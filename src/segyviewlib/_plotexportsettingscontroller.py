from __future__ import division
from PyQt4.QtGui import QCheckBox, QWidget, QComboBox, QDoubleSpinBox, QLabel
from PyQt4.QtGui import QHBoxLayout


class PlotExportSettingsWidget(QWidget):
    def __init__(self, parent, slice_view_widget, context):
        super(PlotExportSettingsWidget, self).__init__(parent)

        self._slice_view_widget = slice_view_widget
        self._context = context

        self._dpi_units = ["in", "cm", "px"]

        if parent is None or self._slice_view_widget is None:
            w, h, dpi = 11.7, 8.3, 100
        else:
            fig = self._slice_view_widget.layout_figure()
            w, h = fig.get_size_inches()
            dpi = fig.dpi

        self._label = QLabel()
        self._label.setDisabled(True)
        self._set_label_txt(w, h, self._dpi_units[0])

        self._fix_size = QCheckBox()
        self._fix_width = QDoubleSpinBox()
        self._fix_width.setDisabled(True)

        self._fix_height = QDoubleSpinBox()
        self._fix_height.setDisabled(True)

        self._fix_dpi_units = QComboBox()
        self._fix_dpi_units.setDisabled(True)

        self._fix_width.setMinimum(1)
        self._fix_width.setMaximum(32000)
        self._fix_width.setValue(w)

        self._fix_height.setMinimum(1)
        self._fix_height.setMaximum(32000)
        self._fix_height.setValue(h)

        self._fix_width.valueChanged.connect(self._fixed_image)
        self._fix_height.valueChanged.connect(self._fixed_image)

        self._fix_dpi_units.addItems(self._dpi_units)
        self._fix_dpi_units.activated.connect(self._fixed_image)
        self._fix_size.toggled.connect(self._fixed_image)

        self._label_widget = self._label
        self._enable_widget = self._fix_size
        self._dpi_widget = self._fix_dpi_units
        self._height_widget = self._fix_height
        self._width_widget = self._fix_width

    @property
    def label(self):
        return self._label_widget

    @property
    def checkbox(self):
        return self._enable_widget

    @property
    def width_spinbox(self):
        return self._width_widget

    @property
    def height_spinbox(self):
        return self._height_widget

    @property
    def units_combobox(self):
        return self._dpi_widget

    @staticmethod
    def to_inches(width, height, dpi, scale):
        if scale == "in":
            return (width, height, dpi)
        elif scale == "cm":
            return (width / 2.54, height / 2.54, dpi)
        elif scale == "px":
            return (width / dpi, height / dpi, dpi)
        else:
            raise NotImplementedError

    def _set_label_txt(self, w, h, scale):
        self._label.setText("{0} x {1} {2}".format(w, h, scale))

    def _fixed_image(self):
        ctx = self._context

        # toggle disabled
        self._fix_height.setDisabled(not self._fix_size.isChecked())
        self._fix_width.setDisabled(not self._fix_size.isChecked())
        self._fix_dpi_units.setDisabled(not self._fix_size.isChecked())
        self._label.setDisabled(not self._fix_size.isChecked())

        if not self._fix_size.isChecked():
            ctx.set_image_size(None)
            return

        w = self._fix_width.value()
        h = self._fix_height.value()
        dpi = 100
        scale = self._fix_dpi_units.currentText()

        self._set_label_txt(w, h, scale)
        ctx.set_image_size(*self.to_inches(w, h, dpi, scale))
