from matplotlib import patches
from matplotlib.ticker import FuncFormatter, AutoLocator
from matplotlib.image import AxesImage
from .slicemodel import SliceModel, SliceDirection
import numpy as np


class SliceView(object):
    def __init__(self, axes, model, interpolation="nearest", aspect="auto"):
        super(SliceView, self).__init__()
        data = np.zeros((1, 1))
        self._image = axes.imshow(data, interpolation=interpolation, aspect=aspect, origin='upper')
        """ :type: AxesImage """
        self._model = model
        """ :type: SliceModel """

        style = {"fill": False,
                 "alpha": 1,
                 "color": 'black',
                 "linestyle": 'dotted',
                 "linewidth": 0.75
                 }

        self._vertical_indicator = patches.Rectangle((-0.5, -0.5), 1, model.height, **style)
        self._horizontal_indicator = patches.Rectangle((-0.5, -0.5), model.width, 1, **style)
        self._zoom_factor = 1.0

        self._view_limits = None

        self._min_xlim = 0
        self._max_xlim = model.width
        self._min_ylim = 0
        self._max_ylim = model.height

    def model(self):
        """ :rtype: SliceModel """
        return self._model

    def create_slice(self, context):
        """ :type context: dict """
        model = self._model
        axes = self._image.axes
        """ :type: matplotlib.axes.Axes """

        axes.set_title(model.title, fontsize=12)
        axes.tick_params(axis='both')
        axes.set_ylabel(model.y_axis_name, fontsize=9)
        axes.set_xlabel(model.x_axis_name, fontsize=9)

        axes.get_xaxis().set_major_formatter(FuncFormatter(model.x_axis_formatter))
        axes.get_xaxis().set_major_locator(AutoLocator())

        axes.get_yaxis().set_major_formatter(FuncFormatter(model.y_axis_formatter))
        axes.get_yaxis().set_major_locator(AutoLocator())

        for label in (axes.get_xticklabels() + axes.get_yticklabels()):
            label.set_fontsize(9)

        self._reset_zoom()

        axes.add_patch(self._vertical_indicator)
        axes.add_patch(self._horizontal_indicator)
        self._update_indicators(context)

        self._image.set_cmap(cmap=context['colormap'])

        self._view_limits = context["view_limits"][self._model.index_direction['name']]

        if model.data is not None:
            self._image.set_data(model.data)

    def data_changed(self, context):
        """ :type context: dict """
        model = self._model
        self._image.set_data(model.data)
        self._image.set_extent((0, model.width, model.height, 0))

    def context_changed(self, context):
        """ :type context: dict """
        self._image.set_cmap(context['colormap'])
        self._image.set_clim(context['min'], context['max'])
        self._image.set_interpolation(context['interpolation'])
        self._update_indicators(context)

        self._set_view_limits()

        if self._model.index_direction is not SliceDirection.depth:
            self._image.axes.set_ylabel(context['samples_unit'])

    def _update_indicators(self, context):
        """ :type context: dict """
        model = self._model
        self._vertical_indicator.set_height(model.height + 1)
        self._vertical_indicator.set_width(1)
        self._horizontal_indicator.set_width(model.width + 1)
        self._horizontal_indicator.set_height(1)

        show_indicators = context['show_indicators']

        self._vertical_indicator.set_visible(model.x_index is not None and show_indicators)
        self._horizontal_indicator.set_visible(model.y_index is not None and show_indicators)

        if model.x_index is not None and show_indicators:
            self._vertical_indicator.set_x(model.x_index)

        if model.y_index is not None and show_indicators:
            self._horizontal_indicator.set_y(model.y_index)

    def _has_view_limits_changed(self):
        return any([self._view_limits.min_xlim != self._min_xlim,
                    self._view_limits.max_xlim != self._max_xlim,
                    self._view_limits.min_ylim != self._min_ylim,
                    self._view_limits.max_ylim != self._max_ylim])

    def _set_view_limits(self, forced_reset=False):

        if self._has_view_limits_changed() or forced_reset:
            self._reset_zoom()

            axes = self._image.axes

            self._min_xlim = self._view_limits.min_xlim
            self._max_xlim = self._view_limits.max_xlim
            axes.set_xlim(self._min_xlim, self._max_xlim)

            self._min_ylim = self._view_limits.min_ylim
            self._max_ylim = self._view_limits.max_ylim
            axes.set_ylim(self._max_ylim, self._min_ylim)  # flipping since y axis is flipped

    def _reset_zoom(self):
        self._zoom_factor = 1

    def zoom(self, x, y, zoom_factor_delta, reset_zoom=False):
        zoom_factor = self._zoom_factor + zoom_factor_delta

        if zoom_factor > 1.0:
            zoom_factor = 1.0
            reset_zoom = True
        elif zoom_factor < 0.25:
            zoom_factor = 0.25

        if abs(zoom_factor - self._zoom_factor) < 0.001:
            return False

        self._zoom_factor = zoom_factor

        if reset_zoom:
            self._set_view_limits(forced_reset=True)
            return True

        model = self._model
        axes = self._image.axes

        new_width = (self._max_xlim - self._min_xlim) * zoom_factor
        new_height = (self._max_ylim - self._min_ylim) * zoom_factor

        cur_xlim = axes.get_xlim()
        cur_ylim = axes.get_ylim()

        relx = (cur_xlim[1] - x) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[0] - y) / (cur_ylim[0] - cur_ylim[1])

        min_zoom_xlim = max(max(0, x - new_width * (1 - relx)), self._min_xlim)
        max_zoom_xlim = min(min(model.width, x + new_width * relx), self._max_xlim)

        max_zoom_ylim = min(min(model.height, y + new_height * rely), self._max_ylim)
        min_zoom_ylim = max(max(0, y - new_height * (1 - rely)), self._min_ylim)

        axes.set_xlim(min_zoom_xlim, max_zoom_xlim)
        axes.set_ylim(max_zoom_ylim, min_zoom_ylim)
        return True

    def pan(self, dx, dy):
        axes = self._image.axes

        xlim = axes.get_xlim()

        if xlim[0] - dx < self._min_xlim:
            dx = xlim[0] - self._min_xlim
        elif xlim[1] - dx > self._max_xlim:
            dx = xlim[1] - self._max_xlim

        ylim = axes.get_ylim()

        if ylim[1] - dy < self._min_ylim:
            dy = ylim[1] - self._min_ylim
        elif ylim[0] - dy > self._max_ylim:
            dy = ylim[0] - self._max_ylim

        axes.set_xlim(xlim - dx)
        axes.set_ylim(ylim - dy)
