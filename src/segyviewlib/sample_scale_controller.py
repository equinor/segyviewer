import sys
from PyQt4.QtGui import QCheckBox, QWidget
from PyQt4.QtGui import QHBoxLayout, QDoubleSpinBox
from PyQt4.QtCore import pyqtSignal, QObject


class SampleScaleController(QObject):
    min_max_changed = pyqtSignal(tuple)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

        self._min_wdgt, self._min_active, self._min_spinbox = self._set_up_opt_spin_box()

        self._min_active.toggled.connect(self._value_changed)
        self._min_spinbox.valueChanged.connect(self._value_changed)

        self._max_wdgt, self._max_active, self._max_spinbox = self._set_up_opt_spin_box()

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

        bundle_widget = self._bundle_widgets(spin_box, check_box)
        return bundle_widget, check_box, spin_box

    def _bundle_widgets(self, spinbox, checkbox=None):
        l = QHBoxLayout()

        if checkbox is not None:
            l.addWidget(checkbox, 0)
        else:
            l.addSpacing(25)
        l.addStretch(0.5)
        l.addWidget(spinbox, 2)
        l.setContentsMargins(0, 0, 0, 0)

        w = QWidget()
        w.setContentsMargins(0, 1, 0, 1)
        w.setLayout(l)
        return w

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
    def min_widget(self):
        return self._min_wdgt

    @property
    def max_widget(self):
        return self._max_wdgt
