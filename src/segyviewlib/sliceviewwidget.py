from PyQt4.QtCore import QPoint
from PyQt4.QtGui import QMenu, QAction
from math import copysign

from segyviewlib import SliceView, LayoutCanvas, SliceModel
from matplotlib.cm import ScalarMappable


class SliceViewWidget(LayoutCanvas):
    def __init__(self, context, width=11.7, height=8.3, dpi=100, parent=None):
        """ :type context: segyviewlib.SliceViewContext """
        super(SliceViewWidget, self).__init__(width, height, dpi, parent)

        self._assigned_slice_models = list(context.models)
        """ :type: list[SliceModel] """
        self._slice_views = {}
        """ :type: dict[matplotlib.axes.Axes,SliceView] """

        self._colormappable = ScalarMappable(cmap=context.colormap)
        self._colormappable.set_array([])

        self._context = context
        context.context_changed.connect(self._context_changed)
        context.data_changed.connect(self._data_changed)
        context.data_source_changed.connect(self._layout_changed)

        self.layout_changed.connect(self._layout_changed)
        self.subplot_pressed.connect(self._subplot_clicked)
        self.subplot_scrolled.connect(self._subplot_scrolled)
        self.subplot_motion.connect(self._subplot_motion)

    def _create_context(self):
        return self._context.create_context(self._assigned_slice_models)

    def _layout_changed(self):
        fig = self.layout_figure()
        axes = fig.layout_axes()
        self._slice_views.clear()

        for model in self._context.models:
            model.visible = False

        for index, ax in enumerate(axes):
            ax.clear()
            if index < len(self._assigned_slice_models):
                model = self._assigned_slice_models[index]
                model.visible = True
                self._slice_views[ax] = SliceView(ax, model)
                self._slice_views[ax].create_slice(self._create_context())

        colormap_axes = self.layout_figure().colormap_axes()
        colorbar = self.layout_figure().colorbar(self._colormappable, cax=colormap_axes, use_gridspec=True)
        colorbar.ax.tick_params(labelsize=9)

        self._context.load_data()
        self._data_changed()

    def _data_changed(self):
        context = self._create_context()
        for slice_view in self._slice_views.values():
            slice_view.data_changed(context)
        self._context_changed()

    def _context_changed(self):
        ctx = self._create_context()
        for slice_view in self._slice_views.values():
            slice_view.context_changed(ctx)

        self._colormappable.set_cmap(ctx['colormap'])
        self._colormappable.set_clim(ctx['min'], ctx['max'])
        self.draw()

    def _create_slice_view_context_menu(self, subplot_index):
        context_menu = QMenu("Slice Model Reassignment Menu", self)

        def reassign(model):
            def fn():
                self._assigned_slice_models[subplot_index] = model
                self._layout_changed()

            return fn

        for model in self._context.models:
            action = QAction(model.title, self)
            action.triggered.connect(reassign(model))
            context_menu.addAction(action)

        return context_menu

    def _subplot_clicked(self, event):
        keys = event['key']

        if self._context.indicators and event['button'] == 1 and not keys:
            x = int(event['x'])
            y = int(event['y'])
            slice_model = self._get_slice_view(event).model()
            self._context.update_index_for_direction(slice_model.x_index_direction, x)
            self._context.update_index_for_direction(slice_model.y_index_direction, y)

        elif event['button'] == 3 and (not keys or keys.state(ctrl=True)):
            subplot_index = event['subplot_index']
            context_menu = self._create_slice_view_context_menu(subplot_index)
            context_menu.exec_(self.mapToGlobal(QPoint(event['mx'], self.height() - event['my'])))

    def _subplot_scrolled(self, event):
        keys = event['key']
        if not keys:
            # at least 1 step per event but a maximum of 5
            step = max(1, abs(int(event['step'])))
            step = min(step, 5)
            step = copysign(step, event['step'])

            slice_model = self._get_slice_view(event).model()
            index = int(slice_model.index + step)

            if 0 <= index < len(slice_model):
                self._context.update_index_for_direction(slice_model.index_direction, index)

        elif keys.state(ctrl=True) or keys.state(shift=True):
            x = event['x']
            y = event['y']
            step = max(1, abs(int(event['step'])))
            step = copysign(step / 20.0, event['step'])

            slice_view = self._get_slice_view(event)

            if slice_view.zoom(x, y, step):
                self._context_changed()

    def _get_slice_view(self, event):
        subplot_index = event['subplot_index']
        fig = self.layout_figure()
        ax = fig.layout_axes()[subplot_index]
        slice_view = self._slice_views[ax]
        return slice_view

    def _subplot_motion(self, event):
        keys = event['key']
        if keys.state(shift=True) or keys.state(ctrl=True):
            dx = event['dx']
            dy = event['dy']

            if dx is not None and dy is not None:
                slice_view = self._get_slice_view(event)
                slice_view.pan(dx, dy)
                self._context_changed()
