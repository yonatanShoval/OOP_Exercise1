# Experiment results

## Setup

All runs below were done on my laptop:

- Windows 10 (build 19045), Intel CPU (Family 6, Model 126)
- Python 3.14.0
- numpy 2.5.4, pynrrd 1.1.3, numba 0.68.0, imageio 2.38.1, imageio-ffmpeg 0.6.0, pillow 13.0.0

## Correctness

All 13 automated tests pass (full output in `tests.txt`). They check exact voxel
values for straight and oblique planes, triangle masking, rounding at the volume
edges, invalid point sets, error frames, and the frame order of a decoded MP4.

The MRI input `examples/MRHead.nrrd` has shape (256, 256, 130) and type int16.
SHA-256 of the file: `e9b54e8855e9024f2238e27224702c1dcb49c64407d937499a3cc42fb1114c8b`.

## Demo videos

| Video | CSV | Frames | Size (width x height) |
| --- | --- | ---: | --- |
| mri_oblique.mp4 | mri_planes.csv | 120 | 122 x 210 |
| mri_triangle.mp4 | triangle_planes.csv | 60 | 112 x 120 |
| analytic_oblique.mp4 | analytic_planes.csv | 60 | 52 x 50 |
| mri_with_errors.mp4 | mri_with_errors.csv | 16 | 122 x 210 |

All videos play at 30 FPS. In `mri_with_errors.mp4`, CSV lines 5, 9, 13 and 17
are invalid on purpose, so they become error frames ("INVALID PLANE" and the
line number). The other 12 rows give normal slices.

I watched the videos: the MRI slices change angle from frame to frame, the
triangle video has black corners outside the triangle, and the error frames
appear exactly where the invalid rows are.

A full run of the MRI demo (120 planes), including loading the file, compiling
the loop and encoding the video, took 3.3 seconds.

## Projection speed

`benchmark.py` uses a 500 x 500 x 500 uint8 volume (125,000,000 bytes). For each
plane type it runs one warm-up, then 5 runs of 100 frames. Only the projection
is timed: no file loading, no compilation and no video encoding.

| Plane | Image (rows x columns) | Median FPS | Slowest run FPS |
| --- | --- | ---: | ---: |
| axis_rectangle | 499 x 500 | 133.4 | 88.3 |
| oblique_rectangle | 499 x 566 | 131.0 | 100.7 |
| triangle | 558 x 500 | 201.4 | 155.1 |

Every run is far above the required 30 FPS, and the median of every plane type
is above the expected 100 FPS. One axis_rectangle run was 88 FPS; the runs vary,
probably because of other programs running on the laptop. All values are in
`benchmark.json`.

## Limitations

- Nearest-voxel sampling can give jagged edges on steep planes.
- Coordinates are voxel indices; voxel spacing from the NRRD header is not used,
  so image proportions can differ from 3D Slicer.
- H.264 video is lossy, so exact pixel values are tested on the raw arrays.
- Gray levels use one min/max range for the whole volume. For signed volumes,
  zero can appear gray instead of black.