import sys
from PyQt4.QtGui import QCheckBox, QWidget
from PyQt4.QtGui import QHBoxLayout, QDoubleSpinBox
from PyQt4.QtCore import pyqtSignal, QObject


class SampleScaleController(QObject):
    min_max_changed = pyqtSignal(tuple)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

        self._min_active, self._min_spinbox = self._set_up_opt_spin_box()

        self._min_active.toggled.connect(self._value_changed)
        self._min_spinbox.valueChanged.connect(self._value_changed)

        self._max_active, self._max_spinbox = self._set_up_opt_spin_box()

        self._max_active.toggled.connect(self._value_changed)
        self._max_spinbox.valueChanged.connect(self._value_changed)

    def _set_up_opt_spin_box(self):
        check_box = QCheckBox()
        spin_box = QDoubleSpinBox()
        spin_box.setDecimals(5)
        spin_box.setSingleStep(0.01)
        spin_box.setMinimum(-sys.float_info.max)
        spin_box.setMaximum(sys.float_info.max)
        spin_box.setDisabled(True)
        check_box.toggled.connect(spin_box.setEnabled)

        return check_box, spin_box

    def _value_changed(self):
        min_value = None
        max_value = None
        if self._min_active.isChecked():
            min_value = self._min_spinbox.value()
            self._max_spinbox.setMinimum(min_value)
        else:
            self._max_spinbox.setMinimum(-sys.float_info.max)

        if self._max_active.isChecked():
            max_value = self._max_spinbox.value()
            self._min_spinbox.setMaximum(max_value)
        else:
            self._min_spinbox.setMaximum(sys.float_info.max)

        self.min_max_changed.emit((min_value, max_value))

    @property
    def min_checkbox(self):
        return self._min_active

    @property
    def min_spinbox(self):
        return self._min_spinbox

    @property
    def max_checkbox(self):
        return self._max_active

    @property
    def max_spinbox(self):
        return self._max_spinbox
