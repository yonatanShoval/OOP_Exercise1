# Plane projection of a 3D volume

Python implementation of Introduction to Software Engineering Exercise 1.
Given an integer NRRD volume and an ordered CSV of planes, the program samples
the volume along each plane and streams one image per plane to an MP4 video.
It follows the assignment's triangle/trapezoid scanline method, with explicitly
documented discretization choices. This is a planar slice, not an X-ray sum or
maximum-intensity projection.

## Windows and VS Code quick start

Use Python 3.12 or 3.13 for a reproducible environment compatible with the
compiled dependencies. Newer Python versions require compatible NumPy/Numba
wheels; the user's existing Python 3.14 installation has not been tested here.
Open this extracted folder in VS Code, then open Terminal > New Terminal.

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

Do not overwrite an existing output. Use another output filename for another run.
The first run includes Numba compilation and takes longer. No 3D Slicer, display
server, or matplotlib is needed. imageio-ffmpeg supplies the FFmpeg executable.
The MP4 already included in `results` can be opened without installing Python.

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

Included: validated models, ordered CSV loading, nearest-neighbour scanline
sampling, unsigned 8/16/32-bit data plus signed 8/16/32-bit compatibility,
global grayscale normalization, constant-size MP4 export, tests and experiment.
Not included: GUI, medical interpretation, physical-space reorientation,
interpolation, X-ray rendering, GPU acceleration or interactive controls.

- `Ex0.py`: command-line entry point; optional `--fps 30` controls playback.
- `volume_project/model.py`: Volume, Plane and CSV loading.
- `volume_project/projector.py`: Projector and the compiled sampling kernel.
- `volume_project/video.py`: GrayMapper and VideoExporter.
- `docs/SRS.md`: requirements and acceptance criteria.
- `docs/ALGORITHM.md`: exact algorithm and ambiguity decisions.
- `docs/DATASET.md`: datasets and provenance.
- `docs/TESTING.md`: strategy and reproducible checks.
- `results/EXPERIMENT.md`: actual environment, correctness and speed results.
- `results/*.mp4`: actual output videos.

## Reproduce checks and examples

```powershell
python -m unittest discover -s tests -v
python make_examples.py
python benchmark.py
python Ex0.py examples/analytic.nrrd examples/analytic_planes.csv analytic.mp4
python Ex0.py examples/MRHead.nrrd examples/triangle_planes.csv triangle.mp4
```

Projection throughput and video playback FPS are different: `--fps` is playback
speed; `benchmark.py` measures actual computation throughput on 500^3 bytes.
Read the measured results and limitations before claiming a performance target.

## Repository

A local Git repository accompanies the archive, with implementation and validation
commits. Commit identity is a neutral placeholder; set your own identity for
future commits. No GitHub repository was created or published.

```powershell
git log --oneline
git config user.name "Your Name"
git config user.email "your@email.example"
```

Third-party libraries handle file reading, numerical storage, compilation and
video encoding. The geometric scanline algorithm is implemented in this project.
All design choices should be reviewed against any additional lecturer guidance.
