# Experiment results

## Actual execution

Executed on the available Linux host, not on the student's Windows machine.
Python: 3.12.14. Platform: Linux-6.18.55-x86_64-with-glibc2.39.
Dependencies: numpy 2.3.5, pynrrd 1.1.3, numba 0.68.0, imageio 2.38.1, imageio-ffmpeg 0.6.0.

## Correctness and end-to-end demonstration

All 12 automated tests passed (see tests.txt). Tests include exact coordinate-coded
oblique sampling, type preservation, mask/bounds and decoded MP4 frame order.
The real MRI source has shape (256, 256, 130) and dtype int16.
SHA-256 of the downloaded NRRD: `e9b54e8855e9024f2238e27224702c1dcb49c64407d937499a3cc42fb1114c8b`.

Actual exported and decoded videos:

| File | Frames | Dimensions | Playback duration at 30 FPS |
| --- | ---: | --- | ---: |
| mri_oblique.mp4 | 120 | 122 x 210 | 4 seconds |
| mri_triangle.mp4 | 60 | 112 x 120 | 2 seconds |
| analytic_oblique.mp4 | 60 | 52 x 50 | 2 seconds |

First, middle and last frames were visually inspected. MRI anatomy is visible,
the sections change with plane angle, triangle masking is present, and frame
sizes remain constant. Array orientation/voxel aspect ratio is not corrected to
clinical physical coordinates. The output therefore illustrates index-space
slicing; it is not a diagnostic viewer.

A fresh subprocess export of the 120-frame MRI demo took 5.388 seconds, including
imports, NRRD read, available cached JIT loading, normalization and H.264 encoding.
This is a total elapsed time, not the pure projection benchmark below.

## Projection throughput

500 x 500 x 500 uint8 volume, 125,000,000 bytes. Each geometry is warmed first,
then measured in five sequential runs of 100 frames. Loading, startup compilation,
normalization and encoding are excluded. This measures our raw projector.

| Geometry | Output rows x columns | Median FPS | Minimum run FPS |
| --- | --- | ---: | ---: |
| axis_rectangle | 499 x 500 | 333.9 | 309.7 |
| oblique_rectangle | 499 x 566 | 356.0 | 323.0 |
| triangle | 558 x 500 | 611.1 | 563.1 |

All tested runs exceeded the assignment's >30 FPS minimum and >=100 FPS expected
projection throughput on this host. This is evidence for these image dimensions
and inputs, not a guarantee for every plane, dtype, CPU or Windows installation.
The constant timing volume has a different cache behavior from arbitrary MRI;
real MRI is used separately for the actual demo. Full run values are retained in
benchmark.json. Benchmarking was performed after replacing per-pixel temporary
arrays with scalar coordinates, without changing the sampling rule.

## Remaining limitations

Nearest-neighbour sampling can alias. Noninteger geometry has the documented
rounding convention. Zero raw background is normalized with the same global
range as other values; signed input can make zero gray. H.264 is lossy. Startup
compilation is slower than warmed projection. Python 3.14 on the student's
machine has not been validated here; dependency installation must succeed there.
No additional lecturer instructions outside the supplied assignment were checked.
