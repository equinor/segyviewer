from PyQt4.QtGui import QCheckBox, QWidget, QLabel
from PyQt4.QtCore import Qt, pyqtSignal, QObject

from segyviewlib import ArraySpinBox


class IndexController(QObject):
    index_changed = pyqtSignal(int)
    min_max_changed = pyqtSignal(tuple)

    def __init__(self, parent=None, context=None, slice_direction_index_source=None):
        QObject.__init__(self, parent)

        self._context = context
        self._slice_direction = slice_direction_index_source

        self._current_index_label = QLabel("")
        self._current_index_label.setDisabled(True)

        # the select-index-widgets
        self.index_s_box = self._set_up_index_widget()

        # the min max settings widgets
        self._min_active, self._min_spinbox = self._set_up_min_max_widgets()
        self._max_active, self._max_spinbox = self._set_up_min_max_widgets()

        self._initialize(self._context.slice_data_source().indexes_for_direction(self._slice_direction).tolist())

    @property
    def index_widget(self):
        return self.index_s_box

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

    @property
    def current_index_label(self):
        return self._current_index_label

    def _set_up_index_widget(self):
        index_s_box = ArraySpinBox([0])
        index_s_box.valueChanged.connect(self.index_changed.emit)
        return index_s_box

    def _set_up_min_max_widgets(self):
        check_box = QCheckBox()
        spin_box = ArraySpinBox([0])
        spin_box.setDisabled(True)

        check_box.toggled.connect(spin_box.setEnabled)
        check_box.toggled.connect(self._min_max_value_changed)
        spin_box.valueChanged.connect(self._min_max_value_changed)

        return check_box, spin_box

    def _initialize(self, indexes):
        self._indexes = indexes
        # set up initial min max values
        self.current_index = 0
        self.min_index = 0
        self.max_index = len(self._indexes) - 1

        self.index_s_box.update_view(self._indexes, self.current_index)

        self._min_spinbox.update_view(self._indexes, self.min_index)
        self._max_spinbox.update_view(self._indexes, self.max_index)

        self._min_spinbox.setMaximum(self.max_index - 1)
        self._max_spinbox.setMinimum(self.min_index + 1)

        self._max_active.setCheckState(Qt.Unchecked)
        self._min_active.setCheckState(Qt.Unchecked)

        self._update_label()
        self._min_max_value_changed()

    @staticmethod
    def _to_lbl_txt(val):
        return str(round(val, 4)) if isinstance(val, float) else str(val)

    def _update_label(self):
        self._current_index_label.setText(
            "pos: {0} - [{1}:{2}]".format(self._to_lbl_txt(self._indexes[self.current_index]),
                                          self._to_lbl_txt(self._indexes[self.min_index]),
                                          self._to_lbl_txt(self._indexes[self.max_index])))

    def update_index(self, index):
        self.index_s_box.update_view(self._indexes, index)
        self.current_index = index
        self._update_label()

    def update_view(self, indexes, index):
        if self._indexes != indexes:
            # re initialize when index is changed
            self._initialize(indexes)
        else:
            self.update_index(index)

    def _min_max_value_changed(self):
        if self._min_active.isChecked():
            self.min_index = self._min_spinbox.value()
            min_max = self.min_index + 1 if self.min_index < self.max_index - 1 else self.max_index
            self._max_spinbox.setMinimum(min_max)

            # move current index to inside the boundary
            if self.min_index > self.current_index:
                self.index_changed.emit(self.min_index)
        else:
            self.min_index = 0

        if self._max_active.isChecked():
            self.max_index = self._max_spinbox.value()
            max_min = self.max_index - 1 if self.max_index > 0 else 0
            self._min_spinbox.setMaximum(max_min)

            # move current index to inside the boundary
            if self.max_index < self.current_index:
                self.index_changed.emit(self.max_index)
        else:
            self.max_index = len(self._indexes) - 1

        self.min_max_changed.emit((self.min_index, self.max_index))
