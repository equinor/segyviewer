from .slicemodel import SliceDirection
import segyio


class SliceDataSource(object):
    def __init__(self, source):
        super(SliceDataSource, self).__init__()

        self._source = source
        """ :type: segyio.SegyFile """

    def read_slice(self, direction, index):
        if direction == SliceDirection.inline:
            iline_index = self._source.ilines[index]
            return self._source.iline[iline_index].T
        elif direction == SliceDirection.crossline:
            xline_index = self._source.xlines[index]
            return self._source.xline[xline_index].T
        elif direction == SliceDirection.depth:
            data = self._source.depth_slice[index]
            if self._source.sorting == segyio.TraceSortingFormat.CROSSLINE_SORTING:
                return data
            else:
                return data.T
        else:
            raise ValueError("Unknown direction: %s" % direction)

    def indexes_for_direction(self, direction):
        if direction == SliceDirection.inline:
            return self._source.ilines
        elif direction == SliceDirection.crossline:
            return self._source.xlines
        elif direction == SliceDirection.depth:
            return list(range(self._source.samples))  # add t0?
        else:
            raise ValueError("Unknown direction: %s" % direction)
