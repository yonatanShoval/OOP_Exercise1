"""Validated input objects; coordinates are voxel indices, not millimetres."""
from dataclasses import dataclass
import csv
import numpy as np
import nrrd


@dataclass(frozen=True)
class Volume:
    data: np.ndarray
    header: dict

    def __post_init__(self):
        if self.data.ndim != 3 or any(not 1 <= s < 1024 for s in self.data.shape):
            raise ValueError('Volume must be 3D with each dimension in [1, 1023]')
        # Signed integers occur in the supplied MRI; support them in addition to unsigned.
        if self.data.dtype.kind not in 'ui' or self.data.dtype.itemsize not in (1, 2, 4):
            raise ValueError('Expected an 8-, 16-, or 32-bit integer volume')

    @classmethod
    def load(cls, path):
        data, header = nrrd.read(str(path), index_order='F')
        return cls(np.ascontiguousarray(data), dict(header))


@dataclass(frozen=True)
class Plane:
    """3 points a,b,c or 4 points a_left,a_right,b,c in voxel-index space."""
    points: tuple

    def __post_init__(self):
        p = np.asarray(self.points, dtype=np.float64)
        if p.shape not in ((3, 3), (4, 3)) or not np.isfinite(p).all():
            raise ValueError('A plane requires 3 or 4 finite 3D points')
        if np.abs(p).max() > 1e6:
            raise ValueError('Coordinates exceed the supported magnitude of 1e6')
        if len(p) == 3:
            left, right, b, c = p[0], p[0], p[1], p[2]
        else:
            left, right, b, c = p
        u, v = b - left, c - right
        length = np.linalg.norm(u)
        if length < 1e-9 or not np.isclose(length, np.linalg.norm(v), rtol=0, atol=0.001):
            raise ValueError('The two nonzero legs must have equal length')
        base = c - b
        width = np.linalg.norm(base)
        if width < 1e-9 or np.linalg.norm(np.cross(u, base)) <= 1e-9 * length * width:
            raise ValueError('Plane points must not be collinear or degenerate')
        if len(p) == 4:
            top = right - left
            top_width = np.linalg.norm(top)
            if top_width < 1e-9 or np.dot(top, base) <= 0:
                raise ValueError('Trapezoid bases must be nonzero and point in the same direction')
            if np.linalg.norm(np.cross(top, base)) > 1e-6 * top_width * width:
                raise ValueError('Trapezoid bases must be parallel')
            # Equal legs alone also permit an oblique parallelogram; reject that ambiguity.
            mid_delta = (b + c - left - right) / 2
            if abs(np.dot(mid_delta, base)) > 1e-6 * np.linalg.norm(mid_delta) * width:
                raise ValueError('Trapezoid must be centred (isosceles)')
        object.__setattr__(self, 'points', tuple(tuple(float(x) for x in q) for q in p))

    def geometry(self):
        p = np.asarray(self.points)
        if len(p) == 3:
            return p[0], p[0], p[1], p[2]
        return tuple(p)

    @property
    def shape(self):
        left, right, b, c = self.geometry()
        return (int(np.ceil(np.linalg.norm(b-left))),
                int(np.ceil(max(np.linalg.norm(right-left), np.linalg.norm(c-b)))) + 1)

@dataclass(frozen=True)
class InvalidPlane:
    line: int
    message: str


def read_planes(path, *, allow_invalid=False):
    """CSV: one plane per row, exactly 9 or 12 numeric fields; no header."""
    planes = []
    with open(path, newline='', encoding='utf-8-sig') as stream:
        for line, row in enumerate(csv.reader(stream), 1):
            if not row or all(not x.strip() for x in row) or row[0].lstrip().startswith('#'):
                continue
            try:
                if len(row) not in (9, 12):
                    raise ValueError('expected 9 or 12 comma-separated coordinates')
                points = np.asarray([float(x) for x in row]).reshape(-1, 3)
                planes.append(Plane(tuple(map(tuple, points))))
            except ValueError as exc:
                message = f'CSV line {line}: {exc}'
                if not allow_invalid:
                    raise ValueError(message) from exc
                planes.append(InvalidPlane(line, str(exc)))
    if not planes:
        raise ValueError('CSV contains no planes')
    return planes
