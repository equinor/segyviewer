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

        self._min_zoom_xlim = None
        self._max_zoom_xlim = None
        self._min_zoom_ylim = None
        self._max_zoom_ylim = None

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

        self._set_default_limits()

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
        self._set_limits()

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

    def _set_default_limits(self):
        self._min_zoom_xlim = None
        self._max_zoom_xlim = None
        self._min_zoom_ylim = None
        self._max_zoom_ylim = None

    def _set_limits(self):
        model = self._model
        axes = self._image.axes

        if self._zoom_factor < 1:  # zoom (and or pan) has precedence over other limits, as long as enabled
            axes.set_xlim(self._min_zoom_xlim, self._max_zoom_xlim)
            axes.set_ylim(self._min_zoom_ylim, self._max_zoom_ylim)
        elif self._view_limits is not None:
            min_x = self._view_limits.min_xlim if self._view_limits.min_xlim is not None else 0
            max_x = self._view_limits.max_xlim if self._view_limits.max_xlim is not None else model.width
            axes.set_xlim(min_x, max_x)

            min_y = self._view_limits.min_ylim if self._view_limits.min_ylim is not None else 0
            max_y = self._view_limits.max_ylim if self._view_limits.max_ylim is not None else model.height
            axes.set_ylim(max_y, min_y)  # flipping since y axis is flipped

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
            self._set_default_limits()
            return True

        model = self._model
        axes = self._image.axes

        new_width = model.width * zoom_factor
        new_height = model.height * zoom_factor

        cur_xlim = axes.get_xlim()
        cur_ylim = axes.get_ylim()

        relx = (cur_xlim[1] - x) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[0] - y) / (cur_ylim[0] - cur_ylim[1])

        self._min_zoom_xlim = max(0, x - new_width * (1 - relx))
        self._max_zoom_xlim = min(model.width, x + new_width * relx)

        self._min_zoom_ylim = min(model.height, y + new_height * rely)
        self._max_zoom_ylim = max(0, y - new_height * (1 - rely))
        return True

    def pan(self, dx, dy):
        axes = self._image.axes
        model = self._model

        xlim = axes.get_xlim()

        if xlim[0] - dx < 0:
            dx = xlim[0]
        elif xlim[1] - dx > model.width:
            dx = xlim[1] - model.width

        ylim = axes.get_ylim()

        if ylim[0] - dy > model.height:
            dy = ylim[0] - model.height
        elif ylim[1] - dy < 0:
            dy = ylim[1]

        self._min_zoom_xlim = xlim[0] - dx
        self._max_zoom_xlim = xlim[1] - dx
        self._min_zoom_ylim = ylim[0] - dy
        self._max_zoom_ylim = ylim[1] - dy
