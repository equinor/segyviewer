from __future__ import print_function

from contextlib import contextmanager

from PyQt4.QtGui import QToolButton, QToolBar, QVBoxLayout, QWidget, QTabWidget
from PyQt4.QtCore import QModelIndex

from segyviewlib import LayoutCombo, SettingsWindow, SliceViewContext
from segyviewlib import SliceDataSource, SliceModel, SliceDirection as SD, resource_icon
from itertools import chain
import os


@contextmanager
def blocked_update(ctxt, current_ctxt):
    blocked = ctxt.signalsBlocked()
    ctxt.blockSignals(ctxt != current_ctxt)
    yield ctxt
    ctxt.blockSignals(blocked)


class SegyTabWidget(QWidget):
    def __init__(self, segywidgets, parent=None):
        QWidget.__init__(self, parent)

        self._segywidgets = segywidgets
        """ :type: list[SegyViewWidget] """

        self._tab_widget = QTabWidget()
        layout = QVBoxLayout()

        for i, segywidget in enumerate(self._segywidgets):
            segywidget.show_toolbar(toolbar=True, layout_combo=False, colormap=True, save=True, settings=True)
            self.modify_qtree(segywidget.settings_window.qtree, [0, 1, 2, 4])
            self._tab_widget.insertTab(i, segywidget, os.path.basename(segywidget.slice_data_source.source_filename))
            segywidget.context.data_changed.connect(self._local_data_changed)

        self._tab_widget.currentChanged.connect(self._tab_changed)

        slice_data_source, slice_models = self.setup_model_source()

        self._context = SliceViewContext(slice_models, slice_data_source, has_data=False)
        self._context.show_indicators(True)
        self._context.data_changed.connect(self.data_changed)

        self._slice_view_widget = None
        self._settings_window = SettingsWindow(self._context, self)
        self._settings_window.min_max_changed.connect(self.min_max_changed)
        self._settings_window.indicators_changed.connect(self.indicators_changed)
        self._settings_window.interpolation_changed.connect(self.interpolation_changed)
        self._settings_window.samples_unit_changed.connect(self.samples_unit_changed)
        self.modify_qtree(self._settings_window.qtree, [3, 5])

        self._toolbar = self._create_toolbar()
        self._local_data_changed(self._segywidgets[0].context.models)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._tab_widget)

        self.setLayout(layout)

    def _local_data_changed(self, models=None):
        for m in self._context.models:
            for current_model in models:
                if current_model.index_direction == m.index_direction:
                    m.index = current_model.index
                if current_model.x_index_direction == m.index_direction:
                    m.x_index = current_model.index
                if current_model.y_index_direction == m.index_direction:
                    m.y_index = current_model.index
            m.dirty = True

        self._update_models()
        self._context.context_changed.emit()

    def data_changed(self):
        self._update_models()
        self._update_views()

    def min_max_changed(self, values, axis):
        min, max = values

        for ctxt in self.ctxs():
            with blocked_update(ctxt, self.current_ctxt()):
                if axis == 'depth':
                    ctxt.set_y_view_limits(SD.crossline, min, max)
                    ctxt.set_y_view_limits(SD.inline, min, max)

                elif axis == 'iline':
                    ctxt.set_x_view_limits(SD.crossline, min, max)
                    ctxt.set_x_view_limits(SD.depth, min, max)

                elif axis == 'xline':
                    ctxt.set_x_view_limits(SD.inline, min, max)
                    ctxt.set_y_view_limits(SD.depth, min, max)

        self._update_views()

    def interpolation_changed(self, interpolation_name):
        for ctxt in self.ctxs():
            with blocked_update(ctxt, self.current_ctxt()):
                ctxt.set_interpolation(interpolation_name)

    def indicators_changed(self, visible):
        for ctxt in self.ctxs():
            with blocked_update(ctxt, self.current_ctxt()):
                ctxt.show_indicators(visible)

    def samples_unit_changed(self, val):
        for ctxt in self.ctxs():
            with blocked_update(ctxt, self.current_ctxt()):
                ctxt.samples_unit = val

    def _update_models(self):
        dirty_models = [m for m in self._context.models if m.dirty]
        local_models = list(chain.from_iterable([ctx.models for ctx in self.ctxs()]))

        for m in dirty_models:
            for local_m in local_models:
                if local_m.index_direction == m.index_direction:
                    local_m.index = m.index
                if local_m.x_index_direction == m.index_direction:
                    local_m.x_index = m.index
                if local_m.y_index_direction == m.index_direction:
                    local_m.y_index = m.index
                local_m.dirty = True
            m.dirty = False

    def _update_views(self):
        self._tab_widget.currentWidget().context.context_changed.emit()
        self._tab_widget.currentWidget().context.load_data()

    def _tab_changed(self):
        widget_spec = self._tab_widget.currentWidget().slice_view_widget.current_layout()
        setting_spec = self.layout_combo.get_current_layout()
        if widget_spec != setting_spec:
            self._tab_widget.currentWidget().slice_view_widget.set_plot_layout(setting_spec)
        self._update_views()

    def setup_model_source(self):
        slice_data_source = SliceDataSource(False)
        directions = [SD.inline, SD.crossline, SD.depth]

        source_template = self._segywidgets[0].slice_data_source

        for direction in directions:
            slice_data_source.set_indexes(direction, source_template.indexes_for_direction(direction))

        inline = SliceModel("Inline", SD.inline, SD.crossline, SD.depth)
        xline = SliceModel("Crossline", SD.crossline, SD.inline, SD.depth)
        depth = SliceModel("Depth", SD.depth, SD.inline, SD.crossline)
        slice_models = [inline, xline, depth]

        return slice_data_source, slice_models

    def _create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        self.layout_combo = LayoutCombo()
        toolbar.addWidget(self.layout_combo)
        self.layout_combo.layout_changed.connect(self.plot_layout_changed)

        self._settings_button = QToolButton()
        self._settings_button.setToolTip("Toggle settings visibility")
        self._settings_button.setIcon(resource_icon("cog.png"))
        self._settings_button.setCheckable(True)
        self._settings_button.toggled.connect(self._show_settings)
        toolbar.addWidget(self._settings_button)

        def toggle_on_close(event):
            self._settings_button.setChecked(False)
            event.accept()

        self._settings_window.closeEvent = toggle_on_close

        return toolbar

    def modify_qtree(self, tree, items):
        for i in items:
            tree.setRowHidden(i, QModelIndex(), True)

    def plot_layout_changed(self, spec):
        self._tab_widget.currentWidget().slice_view_widget.set_plot_layout(spec)

    def _show_settings(self, toggled):
        self._settings_window.setVisible(toggled)
        if self._settings_window.isMinimized():
            self._settings_window.showNormal()

    def current_ctxt(self):
        """
        :rtype: SliceViewContext 
        """
        return self._tab_widget.currentWidget().context

    def ctxs(self):
        """
        :rtype: list of SliceViewContext 
        """
        return [self._tab_widget.widget(index).context for index in range(0, self._tab_widget.count())]
