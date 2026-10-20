"""Scanline algorithm following the assignment; Numba compiles the pixel loop."""
import math
import numpy as np
from numba import njit


@njit(cache=True)
def _scan(data, left, right, b, c, height, width):
    output = np.zeros((height, width), dtype=data.dtype)
    length = math.sqrt(np.sum((b-left)**2))
    for y in range(height):
        # Advance before sampling, as in the supplied pseudocode.
        t = min((y + 1) / length, 1.0)
        start = left + t * (b-left)
        end = right + t * (c-right)
        delta = end-start
        distance = math.sqrt(np.sum(delta**2))
        for step in range(int(math.floor(distance)) + 1):
            p = start if distance < 1e-12 else start + (step / distance) * delta
            column = int(math.floor((width-1-distance)/2 + step + 0.5))
            if column < 0 or column >= width:
                continue
            if not (0 <= p[0] < data.shape[0] and 0 <= p[1] < data.shape[1] and 0 <= p[2] < data.shape[2]):
                continue
            i, j, k = int(math.floor(p[0]+0.5)), int(math.floor(p[1]+0.5)), int(math.floor(p[2]+0.5))
            if i < data.shape[0] and j < data.shape[1] and k < data.shape[2]:
                output[y, column] = data[i, j, k]
    return output


class Projector:
    def __init__(self, max_side=4096):
        self.max_side = max_side

    def project(self, volume, plane):
        height, width = plane.shape
        if height > self.max_side or width > self.max_side:
            raise ValueError(f'Projection exceeds {self.max_side} pixels per side')
        return _scan(volume.data, *plane.geometry(), height, width)
