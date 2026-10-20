"""Create a reproducible analytic NRRD and ordered demo plane CSVs."""
import csv
from pathlib import Path
import numpy as np
import nrrd


def write_planes(path, centre, half_width, height, angles):
    rows = []
    for angle in angles:
        theta = np.deg2rad(angle)
        across = np.array([np.cos(theta), 0, np.sin(theta)]) * half_width
        down = np.array([0, height / 2, 0])
        # a_left, a_right, b, c: rectangles are the limiting isosceles trapezoid case.
        points = [centre-down-across, centre-down+across,
                  centre+down-across, centre+down+across]
        rows.append(np.concatenate(points))
    with open(path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)


def main():
    root = Path(__file__).resolve().parent / 'examples'
    root.mkdir(exist_ok=True)
    x, y, z = np.indices((64, 64, 64), dtype=np.uint32)
    data = (x + 64*y + 4096*z).astype(np.uint32)
    nrrd.write(str(root/'analytic.nrrd'), data, index_order='F')
    write_planes(root/'analytic_planes.csv', np.array([31.5]*3), 25, 50, np.linspace(-55, 55, 60))
    write_planes(root/'mri_planes.csv', np.array([127.5, 127.5, 64.5]), 60, 210, np.linspace(-70, 70, 120))
    # Equilateral triangle rotated about the centre; small enough to remain inside MRI bounds.
    rows = []
    for angle in np.linspace(-50, 50, 60):
        theta = np.deg2rad(angle)
        across = np.array([np.cos(theta), 0, np.sin(theta)]) * 55
        centre = np.array([127.5, 127.5, 64.5])
        a = centre + np.array([0, -70, 0])
        b = centre + np.array([0, 35, 0]) - across
        c = centre + np.array([0, 35, 0]) + across
        rows.append(np.concatenate([a,b,c]))
    with open(root/'triangle_planes.csv', 'w', newline='') as f:
        csv.writer(f).writerows(rows)


if __name__ == '__main__':
    main()
