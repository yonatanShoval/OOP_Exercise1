# Plane projection of a 3D volume

This is my solution to Exercise 1 in Introduction to Software Engineering.

**The problem:** we get a 3D scan (an NRRD file), which is a 3D matrix of numbers.
Each number is the brightness of one voxel. We also get a CSV file where each row
describes a flat cut through the volume, with 3 points (triangle) or 4 points
(trapezoid or rectangle). For every row, the program computes the 2D image of
that cut, and saves all the images as frames of one MP4 video, in the same order.

**How:** the program walks over the cut row by row, as in the algorithm from the
assignment, and takes the value of the closest voxel at every step.
See docs/ALGORITHM.md for the details.

## Windows and VS Code quick start

Tested with Python 3.14 on Windows 10 (see results/EXPERIMENT.md).
Open the project folder in VS Code, then open Terminal > New Terminal.
If installing Numba fails on your Python version, use a Python 3.12 environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe Ex0.py examples\MRHead.nrrd examples\mri_planes.csv my_video.mp4
```

If your current Python is compatible, the simpler alternative is:

```powershell
python -m pip install -r requirements.txt
python Ex0.py examples/MRHead.nrrd examples/mri_planes.csv my_video.mp4
```

Running again with the same output name overwrites the old video.
The first run includes Numba compilation and takes longer.

## CSV contract

One plane per row, no header. Empty rows and rows beginning with # are ignored.
Coordinates are array indices, with data[x,y,z], not physical millimetres.
The format is a project design decision because the assignment leaves it open.

Triangle (9 fields):

```csv
ax,ay,az,bx,by,bz,cx,cy,cz
```

The two legs a->b and a->c must be nonzero, equal in length and noncollinear.

Isosceles trapezoid or rectangle (12 fields):

```csv
left_x,left_y,left_z,right_x,right_y,right_z,bx,by,bz,cx,cy,cz
```

The parallel bases are left->right and b->c, in the same direction.
The equal legs are left->b and right->c. The bases must be centred.
Rectangles are supported as the equal-base special case. Points outside the
volume are permitted; out-of-bounds samples receive zero.

## Scope and deliverables

In scope:

- Reading the NRRD volume (8, 16 or 32 bit integers) and the CSV of planes.
- Checking that every plane is valid, and showing an error frame for a bad row.
- Computing the image of each plane with the closest voxel.
- Saving all the images as one MP4 video.
- Tests, a speed benchmark and an experiment.

Out of scope: a GUI, smoothing between voxels (interpolation), and using the
real size of voxels in millimetres.

Project files:

- `Ex0.py`: command-line entry point; optional `--fps 30` controls playback.
- `volume_project/model.py`: Volume, Plane, InvalidPlaneError and CSV loading.
- `volume_project/projector.py`: Projector and the compiled sampling kernel.
- `volume_project/video.py`: GrayMapper, ErrorFrame and VideoExporter.
- `docs/SRS.md`: requirements and acceptance criteria.
- `docs/ALGORITHM.md`: exact algorithm and ambiguity decisions.
- `docs/DATASET.md`: datasets and provenance.
- `docs/TESTING.md`: strategy and reproducible checks.
- `results/EXPERIMENT.md`: actual environment, correctness and speed results.

## Results

- [Experiment report](results/EXPERIMENT.md)
- [Benchmark results](results/benchmark.json)
- [Test output](results/tests.txt)
- [MRI oblique video](results/mri_oblique.mp4)
- [MRI triangle video](results/mri_triangle.mp4)
- [MRI video with error frames](results/mri_with_errors.mp4)
- [Analytic volume video](results/analytic_oblique.mp4)

## Reproduce checks and examples

```powershell
python -m unittest discover -s tests -v
python make_examples.py
python benchmark.py
python Ex0.py examples/analytic.nrrd examples/analytic_planes.csv analytic.mp4
python Ex0.py examples/MRHead.nrrd examples/triangle_planes.csv triangle.mp4
python Ex0.py examples/MRHead.nrrd examples/mri_with_errors.csv errors.mp4
```

Projection throughput and video playback FPS are different: `--fps` is playback
speed; `benchmark.py` measures actual computation throughput on 500^3 bytes.
Measured results are in results/EXPERIMENT.md.

## Repository

https://github.com/yonatanShoval/OOP_Exercise1

Third-party libraries handle file reading, numerical storage, compilation and
video encoding. The geometric scanline algorithm is implemented in this project.

