# Testing strategy

## Numerical oracle

Use coordinate-coded integer arrays, not screenshots, to verify sampled values.
The axis rectangle test compares against an explicit list of expected coordinates.
The oblique test uses a 3-4-5 direction, so expected coordinates and half-up
rounding can be calculated independently of the projector's geometry routines.
Triangle and trapezoid tests check the last base and empty mask pixels.

## Boundaries and robustness

Check out-of-volume negative coordinates, half-integer rounding, uint8/uint16/
uint32 maxima, signed MRI compatibility, empty or malformed CSV, CSV line numbers,
nonfinite/unequal/collinear geometry, invalid dimensions/dtypes and output limits.
The CLI rejects an output path equal to an input, and overwrites an old output.

## I/O and integration

Round-trip a synthetic NRRD with explicit index order. Run Ex0.main on a temporary
NRRD+CSV, decode the resulting MP4, count all frames and verify even dimensions.
Three planes with increasing intensity check input-frame order after lossy
encoding. Numerical equality is tested on raw arrays, not H.264 frames.

## Demo and visual inspection

Run the exact three-file CLI on real MRI with a rotating four-point CSV, and on
the triangle CSV. Decode and inspect first/middle/last frames of the real demo.
Verify triangle masking, anatomy visible, changing oblique slices, constant
frame dimensions and exact frame counts. This is a visual check, not a medical
orientation or physical aspect-ratio validation.

## Performance

Run benchmark.py on 500^3 uint8 with axis rectangles, oblique rectangles and
triangles; five runs of 100 projections each, after one warmup per geometry.
Report all runs, median, minimum, output sizes and runtime environment. This is
single-process sequential throughput, excluding volume I/O, JIT and encoding.
Measure real video export separately, including startup, if reporting total time.
A result on this host does not guarantee identical Windows performance.

## Reproduction

```text
python -m unittest discover -s tests -v
python benchmark.py
python Ex0.py examples/MRHead.nrrd examples/mri_planes.csv new_mri.mp4
```

No external services or network are needed after dependency installation because
the example data and MP4 outputs are included.
