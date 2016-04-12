#!/usr/bin/env python3


class MultiList(object):
    def __init__(self, xlen, ylen, init=None):
        if init is None:
            self._list = [None] * xlen * ylen
        else:
            self._list = list(init)
        self.xlen = xlen
        self.ylen = ylen

    def __repr__(self):
        return __name__ + ".MultiList({xlen}, {ylen}, {init})".format(
            xlen=repr(self.xlen),
            ylen=repr(self.ylen),
            init=repr(self._list))

    def __str__(self):
        return str(self._list)

    def _slice_from_tuple(self, tup):
        """
        Gives a slice [int * self.xlen:(int + 1) * self.xlen] from (int, None)
        """
        if len(tup) != 2:
            raise TypeError("must be a two tuple")
        if tup[1] is not None:
            raise ValueError("second tuple item must be None")
        index = tup[0]
        return slice(index * self.xlen, (index + 1) * self.xlen)

    def _is_intlike(self, index):
        return (
            isinstance(index, int) or (
                isinstance(index, tuple) and
                len(index) == 2 and
                all((isinstance(x, int) for x in index))))

    def _int_from_tuple(self, tup):
        if not self._is_intlike(tup):
            raise TypeError("`tup` must be 'int' like")
        return tup[0] * self.xlen + tup[1]

    def _int_from_intlike(self, intlike):
        if not self._is_intlike(intlike):
            raise TypeError("`intlike` must be convertable to 'int'")
        if isinstance(intlike, tuple):
            return self._int_from_tuple(intlike)
        else:
            return intlike

    def _is_slicelike_tuple(self, tup):
        return (
            isinstance(tup, tuple) and
            (len(tup) == 2) and
            isinstance(tup[0], int) and
            tup[1] is None)

    def _slice_from_slicelike_tuple(self, tup):
        if not self._is_slicelike_tuple(tup):
            raise TypeError("`tup` must be convertable to 'slice'")
        return slice(tup[0] * self.xlen, (tup[0] + 1) * self.xlen)

    def _is_slicelike_slice(self, slc):
        if not isinstance(slc, slice):
            raise TypeError("`slc` must be 'slice'")
        return (
            all((
                (self._is_intlike(x) or (x is None))
                for x in (slc.start, slc.stop))) and
            (isinstance(slc.step, int) or slc.step is None))

    def _slice_from_slicelike_slice(self, slc):
        if not self._is_slicelike_slice(slc):
            raise TypeError("`slc` must be convertable to a single 'slice'")
        start = slc.start
        if start is not None:
            start = self._int_from_intlike(start)
        stop = slc.stop
        if stop is not None:
            stop = self._int_from_intlike(stop)
        return slice(start, stop, slc.step)

    def _is_multislicelike_slice(self, slc):
        if not isinstance(slc, slice):
            return False
        start = slc.start
        stop = slc.stop
        step = slc.step
        if not (step is None or (isinstance(step, int))):
            return False
        if not all(
                (x is None) or (
                    isinstance(x, tuple) and
                    (len(x) == 2) and
                    (x[1] is None or x[0] is None))
                for x in (start, stop)):
            return False
        return True

    def _slice_iterable_from_multislicelike_slice(self, slc):
        if not self._is_multislicelike_slice(slc):
            raise TypeError(
                "`slc` must be convertable to an interable of 'slice'")

        if isinstance(slc.start, tuple):
            start = slc.start[0]
        else:
            start = slc.start
        if isinstance(slc.stop, tuple):
            stop = slc.stop[0]
        else:
            stop = slc.stop
        step = slc.step
        for y in range(*slice(start, stop, step).indices(self.ylen)):
            yield self._slice_from_tuple((y, None))

    def __getitem__(self, index):
        if self._is_intlike(index):
            index = self._int_from_intlike(index)
        elif self._is_slicelike_tuple(index):
            index = self._slice_from_slicelike_tuple(index)
        elif self._is_slicelike_slice(index):
            index = self._slice_from_slicelike_slice(index)
        elif self._is_multislicelike_slice(index):
            return [
                self._list[x] for x in
                self._slice_iterable_from_multislicelike_slice(index)]
        else:
            raise TypeError()
        return self._list[index]

    def __setitem__(self, index, value):
        if self._is_intlike(index):
            index = self._int_from_intlike(index)
        elif self._is_slicelike_tuple(index):
            index = self._slice_from_slicelike_tuple(index)
        elif self._is_slicelike_slice(index):
            index = self._slice_from_slicelike_slice(index)
        elif self._is_multislicelike_slice(index):
            for slc, value in zip(
                    self._slice_iterable_from_multislicelike_slice(index),
                    value):
                self._list[slc] = value
        else:
            raise TypeError()
        self._list[index] = value
