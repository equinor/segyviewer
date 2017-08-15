from PyQt4.QtGui import QFileDialog, QToolButton, QToolBar, QVBoxLayout, QWidget, QWidgetAction

from segyviewlib import ColormapCombo, LayoutCombo, SettingsWindow, SliceViewContext, HelpWindow
from segyviewlib import SliceDataSource, SliceModel, SliceDirection as SD, SliceViewWidget, resource_icon


class SegyViewWidget(QWidget):
    def __init__(self, filename, show_toolbar=True, color_maps=None,
                 width=11.7, height=8.3, dpi=100,
                 segyioargs={}, parent=None):
        QWidget.__init__(self, parent)

        inline = SliceModel("Inline", SD.inline, SD.crossline, SD.depth)
        xline = SliceModel("Crossline", SD.crossline, SD.inline, SD.depth)
        depth = SliceModel("Depth", SD.depth, SD.inline, SD.crossline)

        slice_models = [inline, xline, depth]
        slice_data_source = SliceDataSource(filename, **segyioargs)
        self._slice_data_source = slice_data_source

        self._context = SliceViewContext(slice_models, slice_data_source)
        self._context.show_indicators(True)

        self._slice_view_widget = SliceViewWidget(self._context, width, height, dpi, self)

        layout = QVBoxLayout()

        self._settings_window = SettingsWindow(self._context, self)
        self._help_window = HelpWindow(self)

        self._toolbar = self._create_toolbar(color_maps)
        self._toolbar.setVisible(show_toolbar)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._slice_view_widget)

        self.setLayout(layout)

    @property
    def context(self):
        """ :rtype: SliceViewContext"""
        return self._context

    @property
    def slice_data_source(self):
        """ :rtype: SliceDataSource"""
        return self._slice_data_source

    @property
    def toolbar(self):
        """ :rtype: QToolBar """
        return self._toolbar

    @property
    def slice_view_widget(self):
        """ :rtype: SliceViewWidget """
        return self._slice_view_widget

    @property
    def settings_window(self):
        """ :rtype: QWidget """
        return self._settings_window

    @property
    def help_window(self):
        """ :rtype: QWidget """
        return self._help_window

    # custom signal slots are required to be manually disconnected
    # https://stackoverflow.com/questions/15600014/pyqt-disconnect-slots-new-style
    def __del__(self):
        self._layout_combo.layout_changed.disconnect(self._slice_view_widget.set_plot_layout)

    def _create_toolbar(self, color_maps):
        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setMovable(False)

        self._layout_combo = LayoutCombo()
        self._layout_combo_action = QWidgetAction(self._layout_combo)
        self._layout_combo_action.setDefaultWidget(self._layout_combo)
        toolbar.addAction(self._layout_combo_action)
        self._layout_combo.layout_changed.connect(self._slice_view_widget.set_plot_layout)

        # self._colormap_combo = ColormapCombo(['seismic', 'spectral', 'RdGy', 'hot', 'jet', 'gray'])
        self._colormap_combo = ColormapCombo(color_maps)
        self._colormap_combo.currentIndexChanged[int].connect(self._colormap_changed)
        toolbar.addWidget(self._colormap_combo)

        self._save_button = QToolButton()
        self._save_button.setToolTip("Save as image")
        self._save_button.setIcon(resource_icon("table_export.png"))
        self._save_button.clicked.connect(self._save_figure)
        toolbar.addWidget(self._save_button)

        self._settings_button = QToolButton()
        self._settings_button.setToolTip("Toggle settings visibility")
        self._settings_button.setIcon(resource_icon("cog.png"))
        self._settings_button.setCheckable(True)
        self._settings_button.toggled.connect(self._show_settings)
        toolbar.addWidget(self._settings_button)

        self._help_button = QToolButton()
        self._help_button.setToolTip("View help")
        self._help_button.setIcon(resource_icon("help.png"))
        self._help_button.setCheckable(True)
        self._help_button.toggled.connect(self._show_help)
        toolbar.addWidget(self._help_button)

        def toggle_on_close(event):
            self._settings_button.setChecked(False)
            event.accept()

        def toggle_on_close_help(event):
            self._help_button.setChecked(False)
            event.accept()

        self._settings_window.closeEvent = toggle_on_close
        self._help_window.closeEvent = toggle_on_close_help

        self._colormap_combo.setCurrentIndex(45)
        self.set_default_layout()

        return toolbar

    def _colormap_changed(self, index):
        colormap = str(self._colormap_combo.itemText(index))
        self._context.set_colormap(colormap)

    def _interpolation_changed(self, index):
        interpolation_name = str(self._interpolation_combo.itemText(index))
        self._context.set_interpolation(interpolation_name)

    def _save_figure(self):
        formats = "Portable Network Graphic (*.png);;Adobe Acrobat (*.pdf);;Scalable Vector Graphics (*.svg)"
        output_file = QFileDialog.getSaveFileName(self, "Save as image", "untitled.png", formats)

        output_file = str(output_file).strip()

        if len(output_file) == 0:
            return

        image_size = self._context.image_size
        if not image_size:
            fig = self._slice_view_widget
        else:
            w, h, dpi = image_size
            fig = SliceViewWidget(self._context, width=w, height=h, dpi=dpi)
            fig.set_plot_layout(self._slice_view_widget.layout_figure().current_layout())

        fig.layout_figure().savefig(output_file)

    def set_source_filename(self, filename):
        self._slice_data_source.set_source_filename(filename)

    def set_default_layout(self):
        # default slice view layout depends on the file size
        if self._slice_data_source.file_size < 8 * 10 ** 8:
            self._layout_combo.setCurrentIndex(self._layout_combo.DEFAULT_SMALL_FILE_LAYOUT)
        else:
            self._layout_combo.setCurrentIndex(self._layout_combo.DEFAULT_LARGE_FILE_LAYOUT)

    def as_depth(self):
        self._context.samples_unit = 'Depth (m)'

    def _show_settings(self, toggled):
        self._settings_window.setVisible(toggled)
        if self._settings_window.isMinimized():
            self._settings_window.showNormal()

    def _show_help(self, toggled):
        self._help_window.setVisible(toggled)
        if self._help_window.isMinimized():
            self._help_window.showNormal()

    def show_toolbar(self, toolbar, layout_combo=True, colormap=True, save=True, settings=True):
        self._toolbar.setVisible(toolbar)
        self._colormap_combo.setDisabled(not colormap)
        self._save_button.setDisabled(not save)
        self._settings_button.setDisabled(not settings)
        self._layout_combo_action.setVisible(layout_combo)
