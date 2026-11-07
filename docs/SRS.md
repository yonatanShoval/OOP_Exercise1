# Software Requirements Specification

## Purpose

Produce 2D planar images from a 3D integer raster, then export exactly one video
frame per CSV plane, in input order. The primary quality goals are correct
sampling, explicit design, maintainable objects and measured runtime efficiency.

## Inputs and outputs

Input 1 is an NRRD with three dimensions, each between 1 and 1023 inclusive.
Unsigned 8-, 16- and 32-bit integers are required; signed equivalents are accepted
for compatibility with real MRI files. Other data types are rejected.
Input 2 is UTF-8 CSV as specified in README, with 9 or 12 finite numeric fields
per non-comment row. Input 3 is the .mp4 output path. Output is H.264 video,
yuv420p, at 30 playback FPS by default. The CLI permits another positive FPS.

## Functional requirements

FR1. Read NRRD preserving its array-axis ordering via index_order='F'.
FR2. Validate every plane and raise InvalidPlaneError for unequal legs,
degenerate triangles, crossed/nonparallel or noncentred trapezoids, a top edge
longer than the base, nonfinite coordinates and malformed rows.
Unsupported volumes and an empty CSV are also rejected.
FR3. Sample three-point triangles and four-point isosceles trapezoids according
to the detailed scanline algorithm. Rectangles are allowed.
FR4. Use nearest-neighbour voxel sampling with explicit rounding. Samples outside
the index volume, and unused triangle pixels, are zero in the raw image.
FR5. Preserve original integer values and dtype in raw projection matrices.
FR6. Normalize using one min/max range from the whole volume; a constant volume
maps to black. Export centered frames on one common, even-sized black canvas.
FR7. Output exactly one frame per plane, preserving order without interpolation.
FR8. In the CLI, an invalid plane does not stop the run: its frame becomes an
error frame (black, white X, "INVALID PLANE" and the CSV line number), a warning
is printed, and the other planes are rendered normally. Input or output errors
(missing file, bad volume, empty CSV, wrong extension) stop the run with a
one-line message and exit status 1. An existing output file is overwritten.
FR9. Provide deterministic data generation, automated tests, a demo and experiment.

## Nonfunctional requirements

NFR1. Measure the assignment's >30 FPS minimum and >=100 FPS expected projection
throughput on a 500^3-byte volume. Record image dimensions, warmup and hardware.
NFR2. Exclude NRRD loading, JIT startup and video encoding from that projection
measurement; report the exclusion. End-to-end export is a separate measurement.
NFR3. Stream frames to bound memory rather than store an entire video in RAM.
NFR4. Each image dimension must be at most 4096; reject larger requests before
projection/video allocation. Limit absolute coordinates to 1e6. These are project
resource limits, not constraints copied from the assignment.
NFR5. Keep input, geometry, projection, intensity mapping and export responsibilities
separate. Avoid repeating input loads or global min/max per video frame.

## Acceptance

Run the documented three-positional-argument command. The video must decode,
contain the CSV's plane count and preserve frame order. Exact synthetic values
must match independently calculated axis-aligned and oblique samples. Invalid
inputs must fail predictably. Run and record the benchmark rather than infer
speed from a playback FPS setting.

## Assumptions and limits

Voxel spacing, origin and direction are retained in the header but not applied:
the assignment describes indices into M. A physically proportioned or clinically
oriented slice would need another coordinate transform. Nearest-neighbour
sampling may alias. H.264 is lossy. Zero-valued raw pixels are mapped using the
same intensity scale as the volume; for a signed volume this may be gray.
Encoder failure can leave an incomplete MP4 that must be removed before retry.
NRRD and CSV inputs are trusted local assignment datasets, not a hostile-file
service. No medical suitability is claimed.
