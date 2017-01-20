from PyQt4.QtGui import QCheckBox, QWidget, QFormLayout, QComboBox, QLabel, QDoubleSpinBox
from PyQt4.QtGui import QPushButton, QHBoxLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt4.QtCore import Qt, QObject

from segyviewlib import SliceDirection, SampleScaleController, IndexController


class SettingsWindow(QWidget):
    def __init__(self, context, parent=None):
        """
        :type context: segyviewlib.SliceViewContext
        :type parent: QObject
        """
        QWidget.__init__(self, parent, Qt.WindowStaysOnTopHint | Qt.Window)
        self.setVisible(False)

        self._context = context
        self._context.context_changed.connect(self._settings_changed)
        self._context.data_changed.connect(self._settings_changed)
        self._context.data_source_changed.connect(self._settings_changed)

        f_layout = QFormLayout()

        self._iline_count = QLabel("")
        self._xline_count = QLabel("")
        self._offset_count = QLabel("")
        self._sample_count = QLabel("")
        self._minimum_value = QLabel("")
        self._maximum_value = QLabel("")

        f_layout.addRow("Inline Count:", self._iline_count)
        f_layout.addRow("Crossline Count:", self._xline_count)
        f_layout.addRow("Offset Count:", self._offset_count)
        f_layout.addRow("Sample Count:", self._sample_count)
        f_layout.addRow("Minimum Value:", self._minimum_value)
        f_layout.addRow("Maximum Value:", self._maximum_value)

        # iline
        self._il_controller = IndexController(parent=self,
                                              context=self._context,
                                              slice_direction_index_source=SliceDirection.inline)
        self._il_controller.index_changed.connect(self._index_changed_fn(SliceDirection.inline))
        self._il_controller.min_max_changed.connect(self.iline_constraint_changed)

        # xline
        self._xl_controller = IndexController(parent=self,
                                              context=self._context,
                                              slice_direction_index_source=SliceDirection.crossline)
        self._xl_controller.index_changed.connect(self._index_changed_fn(SliceDirection.crossline))
        self._xl_controller.min_max_changed.connect(self.xline_constraint_changed)

        # depth
        self._depth_controller = IndexController(parent=self,
                                                 context=self._context,
                                                 slice_direction_index_source=SliceDirection.depth)
        self._depth_controller.index_changed.connect(self._index_changed_fn(SliceDirection.depth))
        self._depth_controller.min_max_changed.connect(self.depth_constraint_changed)

        # sample
        self._sample_controller = SampleScaleController(self)
        self._sample_controller.min_max_changed.connect(self.sample_constraint_changed)

        self._symmetric_scale = QCheckBox()
        self._symmetric_scale.toggled.connect(self._context.set_symmetric_scale)

        # view
        self._indicator_visibility = QCheckBox()
        self._indicator_visibility.toggled.connect(self._context.show_indicators)

        self._interpolation_combo = QComboBox()
        self._interpolations_names = ['nearest', 'catrom', 'sinc']
        self._interpolation_combo.addItems(self._interpolations_names)
        self._interpolation_combo.currentIndexChanged.connect(self._interpolation_changed)

        # plot export settings
        self._plt_settings_wdgt = PlotExportSettingsWidget(self, parent._slice_view_widget, self._context)

        # define tree layout

        tree_def = {"": [
            {"Inline": [
                {"": self._il_controller.current_index_label},
                {"Inline:": self._il_controller.index_widget},
                {"Minimum:": self._il_controller.min_widget},
                {"Maximum:": self._il_controller.max_widget}
            ]
            },
            {"Crossline": [
                {"": self._xl_controller.current_index_label},
                {"Crossline": self._xl_controller.index_widget},
                {"Minimum:": self._xl_controller.min_widget},
                {"Maximum:": self._xl_controller.max_widget}
            ]
            },
            {"Depth": [
                {"": self._depth_controller.current_index_label},
                {"Depth:": self._depth_controller.index_widget},
                {"Minimum:": self._depth_controller.min_widget},
                {"Maximum:": self._depth_controller.max_widget}
            ]
            },
            {"Sample": [
                {"Custom min.:": self._sample_controller.min_widget},
                {"Custom max.:": self._sample_controller.max_widget},
                {"Symmetric scale:": self._symmetric_scale}
            ]
            },
            {"View": [
                {"Show Indicators:": self._indicator_visibility},
                {"Interpolation Type:": self._interpolation_combo}
            ]
            },
            {"Plot export": [
                {"Fixed width x height:": self._plt_settings_wdgt.width_height_widget},
                {"Unit:": self._plt_settings_wdgt.units_widget}
            ]
            }
        ]}

        # setup the menu/navigation tree widget
        tre = QTreeWidget(self)
        tre.setHeaderHidden(True)
        tre.setColumnCount(2)
        tre.setMinimumSize(350, 600)
        tre.setColumnWidth(0, 200)
        tre.setColumnWidth(1, 150)

        self._build_tree(tre, tree_def, tre.invisibleRootItem())

        # layout
        vertical_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        vertical_layout.addLayout(f_layout, 0)
        vertical_layout.addStretch()
        vertical_layout.addWidget(tre, 1)
        vertical_layout.addStretch()
        vertical_layout.addLayout(button_layout, 0)

        self.setLayout(vertical_layout)
        self.setMinimumSize(400, 930)

    def _create_user_value(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

    def _build_tree(self, tree_wdgt, tree_def, root):
        parent, children = tree_def.items()[0]

        # empty label /parent is a special case: either inline with the previous, or skip
        if parent == "":
            if isinstance(children, QWidget):
                item = root
                tree_wdgt.setItemWidget(item, 1, children)

            elif isinstance(children, list):
                for c in children:
                    self._build_tree(tree_wdgt, c, root)
        else:
            item = QTreeWidgetItem(root)
            item.setText(0, parent)
            item.setExpanded(True)

            if isinstance(children, list):
                for c in children:
                    self._build_tree(tree_wdgt, c, item)
            else:
                tree_wdgt.setItemWidget(item, 1, children)

    def add_empty_row(self, layout, legend=""):
        layout.addRow(legend, QLabel())

    def _settings_changed(self):
        ctx = self._context
        self._indicator_visibility.setChecked(ctx.indicators)

        index = self._interpolations_names.index(ctx.interpolation)
        self._interpolation_combo.setCurrentIndex(index)

        self._symmetric_scale.setChecked(ctx.symmetric_scale)

        ilines, xlines, offsets, samples = ctx.slice_data_source().dims()
        self._iline_count.setText("%d" % ilines)
        self._xline_count.setText("%d" % xlines)
        self._offset_count.setText("%d" % offsets)
        self._sample_count.setText("%d" % samples)

        self._minimum_value.setText("%f" % ctx.global_minimum)
        self._maximum_value.setText("%f" % ctx.global_maximum)

        indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.inline).tolist()
        index = ctx.index_for_direction(SliceDirection.inline)
        self._il_controller.update_view(indexes, index)

        indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.crossline).tolist()
        index = ctx.index_for_direction(SliceDirection.crossline)
        self._xl_controller.update_view(indexes, index)

        indexes = ctx.slice_data_source().indexes_for_direction(SliceDirection.depth).tolist()
        index = ctx.index_for_direction(SliceDirection.depth)
        self._depth_controller.update_view(indexes, index)

    def _interpolation_changed(self, index):
        interpolation_name = str(self._interpolation_combo.itemText(index))
        self._context.set_interpolation(interpolation_name)

    def _index_changed_fn(self, direction):
        def fn(value):
            self._context.update_index_for_direction(direction, value)

        return fn

    def sample_constraint_changed(self, values):
        self._context.set_user_values(*values)

    def depth_constraint_changed(self, values):
        min, max = values
        self._context.set_y_index_constraint(SliceDirection.crossline, min, max)
        self._context.set_y_index_constraint(SliceDirection.inline, min, max)

    def iline_constraint_changed(self, values):
        min, max = values
        self._context.set_x_index_constraint(SliceDirection.crossline, min, max)

    def xline_constraint_changed(self, values):
        min, max = values
        self._context.set_x_index_constraint(SliceDirection.inline, min, max)


class PlotExportSettingsWidget(QWidget):
    def __init__(self, parent, slice_view_widget, context):
        super(PlotExportSettingsWidget, self).__init__(parent)

        self._slice_view_widget = slice_view_widget
        self._context = context

        self._dpi_units = ["in", "cm", "px"]
        self._fix_size = QCheckBox()
        self._fix_width = QDoubleSpinBox()
        self._fix_width.setDisabled(True)
        self._fix_height = QDoubleSpinBox()
        self._fix_height.setDisabled(True)

        self._fix_dpi_units = QComboBox()
        self._fix_dpi_units.setDisabled(True)

        self.dpi_wdgt = QWidget()
        dpi_l = QHBoxLayout()
        dpi_l.addSpacing(25)
        dpi_l.addStretch(0.5)
        dpi_l.addWidget(self._fix_dpi_units, 2)
        dpi_l.setContentsMargins(0, 0, 0, 0)
        self.dpi_wdgt.setLayout(dpi_l)

        if parent is None:
            w, h, dpi = 11.7, 8.3, 100
        else:
            fig = self._slice_view_widget.layout_figure()
            w, h = fig.get_size_inches()
            dpi = fig.dpi

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

        self.fix_wdgt = QWidget()
        self._fix_size.setContentsMargins(0, 1, 0, 1)
        self._fix_width.setContentsMargins(0, 1, 0, 1)
        self._fix_height.setContentsMargins(0, 10, 0, 1)

        wxh_layout = QHBoxLayout()
        wxh_layout.setContentsMargins(0, 0, 0, 0)
        wxh_layout.addWidget(self._fix_size)
        wxh_layout.addWidget(self._fix_width)
        wxh_layout.addWidget(self._fix_height)
        self.fix_wdgt.setLayout(wxh_layout)

    @property
    def width_height_widget(self):
        return self.fix_wdgt

    @property
    def units_widget(self):
        return self.dpi_wdgt

    @staticmethod
    def to_inches(width, height, dpi, scale):
        if scale == "in":
            return (width, height, dpi)
        elif scale == "cm":
            return (width / 2.54, height / 2.54, dpi)
        elif scale == "px":
            return (int(width) / dpi, int(height) / dpi, dpi)
        else:
            raise NotImplementedError

    def _fixed_image(self):
        ctx = self._context

        # toggle disabled
        self._fix_height.setDisabled(not self._fix_size.isChecked())
        self._fix_width.setDisabled(not self._fix_size.isChecked())
        self._fix_dpi_units.setDisabled(not self._fix_size.isChecked())

        if not self._fix_size.isChecked():
            ctx.set_image_size(None)

            return

        w = self._fix_width.value()
        h = self._fix_height.value()
        dpi = 100
        scale = self._fix_dpi_units.currentText()

        ctx.set_image_size(*self.to_inches(w, h, dpi, scale))
