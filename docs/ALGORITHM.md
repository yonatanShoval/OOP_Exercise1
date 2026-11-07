# Scanline projection algorithm

## Objects and responsibilities

- Volume: holds the 3D array data[x,y,z] and the file header.
- Plane: checks the points and gives the corners and the image size.
- Projector: computes the image of one plane.
- GrayMapper: turns voxel values into gray levels 0..255.
- ErrorFrame: draws the black frame with an X for an invalid plane.
- VideoExporter: writes all frames to the MP4 file.
- Ex0: reads the command line and connects all of these.

## Geometry

For a triangle, both legs start at the apex a: left = right = a, and the legs
end at b and c. For a trapezoid, the left leg is left->b and the right leg is
right->c.

L = |b-left| = |c-right| is the leg length, B0 = |right-left| is the top edge,
and B1 = |c-b| is the base.

Image height H = ceil(L), image width W = ceil(max(B0, B1)) + 1.
We round the sizes up because lengths are usually not whole numbers, and we add
one column so that both ends of the base fit in the image.

Images are stored as [row, column]. The assignment writes E[x][y]; this is only
a different order of writing, not a different image.

## Sampling

Start with an H x W image full of zeros (black). Then, for every row y from 0 to H-1:

1. Move one step down both legs. Like the assignment, we step first and then
   read, so the first row is already one step below the top. The last step is
   cut so we never go past b and c.
   t = min((y+1)/L, 1)
   start = left + t*(b-left),  end = right + t*(c-right)
2. Walk on the straight line from start to end, in steps of length 1.
   If start and end are the same point, take just that one point.
   d = |end-start|,  direction = (end-start)/d  (a step of length 1)
   p = start + s*direction  for s = 0, 1, ..., floor(d)
3. Each p usually has fractions, for example (41.3, 87.8, 59.6). Round each
   coordinate to the closest integer to get a voxel, here (41, 88, 60).
4. If this voxel is inside the volume, take its value. If not, keep 0.
   So a point less than half a voxel outside still gets the edge voxel.
5. Write the value in row y. Each row is centred, so a triangle does not lean
   to one side.
   column = floor((W-1-d)/2 + s + 0.5)

Rounding: a value exactly in the middle, like 2.5, goes up to 3. We do not use
Python's round(), because round(2.5) gives 2.

Every point is computed from the start of its row (start + s*direction), not by
adding dp again and again, so small errors do not add up.

## Decisions completing the assignment

- Closest voxel: a point with fractions takes the value of the closest voxel.
  The lecturer's Q&A says this is the simple and proper way, with no need for
  super resolution.
- Outside the volume: the value is 0, as in the assignment (v=0 if p is not in M).
  In the video this is black.
- Invalid planes: if the points are not valid (EPS = 0.001), Plane raises
  InvalidPlaneError, as the Q&A asks. In the demo, that CSV row becomes an error
  frame, and the other rows are processed normally.
- Top edge: the Q&A says the top edge (a1->a2) can't be longer than the base
  (b->c), so we raise an error in that case.
- Isosceles trapezoid: the top edge and the base must be parallel, point the
  same way and be centred. A slanted parallelogram also has equal legs, but it is
  not an isosceles trapezoid, so we reject it. Rectangles are allowed.
- CSV format: no header line, 9 numbers (triangle) or 12 numbers (trapezoid) in
  each row, and one row is one frame. The assignment does not fix the format.
- Coordinates are voxel indices into M, like in the assignment, not millimetres.
- Same frame size: images of different sizes are centred on one black frame,
  because all frames of a video must have the same size.
- Gray levels: values are mapped to 0..255 with one min and one max for the whole
  volume, so the same tissue has the same gray in every frame. The video is
  H.264, which is lossy, so exact values are tested on the raw images.

## Efficiency

The pixel loop is our own code, not a ready-made slicing function. It is
compiled with Numba, so it runs fast. The plane checks run once per plane,
outside the loop. Each frame costs O(H*W) time and memory, and frames are
written to the video one by one instead of being kept in memory.
Measured speed: results/EXPERIMENT.md.