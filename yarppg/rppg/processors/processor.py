"""Provides base classes for rPPG processors."""
import dataclasses
from typing import Any, Dict

import numpy as np


@dataclasses.dataclass
class ProcessorConfig:
    name: str
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)


class Processor:
    def __init__(self):
        self.name = None
        self._rs = []
        self._gs = []
        self._bs = []

        self.vs = []

    def calculate(self, roi):  # noqa: ARG002
        return np.nan

    def __call__(self, roi):
        v = self.calculate(roi)
        self.vs.append(v)
        return v

    def spatial_pooling(self, roi, append_rgb=False):
        r, g, b = roi.get_mean_rgb()

        if append_rgb:
            self._rs.append(r)
            self._gs.append(g)
            self._bs.append(b)

        return r, g, b

    def __str__(self):
        if self.name is None:
            return "Processor"
        else:
            return self.name

    @staticmethod
    def moving_average_update(xold, xs, winsize):  # noqa: ARG004
        if len(xs) == 0:
            return np.nan
        """
        n = len(xs)
        if n == 0:
            return 0
        if n < winsize:
            return sum(xs) / len(xs)
        return xold + (xs[-1] - xs[max(0, n - winsize)]) / min(n, winsize)
        """
        return np.nanmean(xs[-winsize:])


class FilteredProcessor(Processor):
    def __init__(self, processor, filtfun):
        Processor.__init__(self)
        self._processor = processor
        self._filtfun = filtfun
        self.name = "Filtered" + str(processor)

    def calculate(self, roi):
        v = self._filtfun(self._processor.calculate(roi))
        return v
