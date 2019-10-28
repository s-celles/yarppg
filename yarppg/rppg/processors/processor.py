import cv2
import numpy as np


class Processor:
    def __init__(self):
        self.name = None
        self._rs = []
        self._gs = []
        self._bs = []

        self.vs = []

    def calculate(self, roi):
        self.vs.append(np.nan)
        return self.vs[-1]

    def __call__(self, roi):
        return self.calculate(roi)

    def spatial_pooling(self, roi_pixels, append_rgb=False):
        if roi_pixels.shape[:2] == (0, 0):
            r, g, b = np.nan, np.nan, np.nan
        else:
            b, g, r, a = cv2.mean(roi_pixels)

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
    def moving_average_update(xold, xs, winsize):
        if len(xs) == 0:
            return np.nan
        '''
        n = len(xs)
        if n == 0:
            return 0
        if n < winsize:
            return sum(xs) / len(xs)
        return xold + (xs[-1] - xs[max(0, n - winsize)]) / min(n, winsize)
        '''
        return np.nanmean(xs[-winsize:])