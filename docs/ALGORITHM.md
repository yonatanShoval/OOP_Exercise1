# Scanline projection algorithm

## Objects and responsibilities

Volume owns a contiguous data[x,y,z] array and metadata. Plane validates geometry
and supplies scan endpoints and image shape. Projector computes raw images.
GrayMapper converts integer intensities for display. VideoExporter creates a
common canvas and streams frames. Ex0 wires these objects together.

## Geometry

For a triangle, left=right=a, with endpoints b,c. For a trapezoid use the four
ordered points left,right,b,c. Let L=|b-left|=|c-right|, B0=|right-left|,
B1=|c-b|. Reject degenerate or invalid geometry.
Height H=ceil(L), width W=ceil(max(B0,B1))+1. The extra column explicitly includes
both endpoints when a base has integral length. Arrays are stored [row,column],
while the assignment writes E[x][y]; this is a storage convention only.

## Sampling

Initialize a zero H by W array of the volume's dtype. For row y in 0..H-1:

1. t=min((y+1)/L,1). This advances along the legs before sampling, matching the
   supplied pseudocode. Clamp the fractional final step to avoid overshooting.
2. start=left+t*(b-left); end=right+t*(c-right).
3. d=|end-start|; direction=(end-start)/d when d>0.
4. For integer s from 0 through floor(d), sample p=start+s*direction.
   A zero-width row uses start once, avoiding division by zero.
5. Center it at column floor((W-1-d)/2+s+0.5).
6. Reject p outside continuous index bounds [0,sx) x [0,sy) x [0,sz).
   Round each coordinate with floor(value+0.5), then check discrete bounds again.
   If either bounds check fails, leave zero. Otherwise store M[i,j,k].

Nearest-neighbour rounding uses ties toward the greater integer. It does not use
Python round(), whose half-to-even behavior would make a different convention.
No accumulated p+=dp error: every point is computed from the row start.
Floating-point representations near a boundary can still change a rounded sample.

## Decisions completing the assignment

- CSV has no header, exactly 9 or 12 fields per plane, one row per video frame.
- Coordinates refer to voxel indices; do not apply physical NRRD transforms.
- The first row follows the supplied advance-before-read loop, so the apex/top
  edge is not a separate row. The final fractional step is clamped.
- ceil sizes and an inclusive base endpoint remove noninteger dimension ambiguity
  and the endpoint overrun in the pseudocode's Dbc-wide output with x1<=d12.
- Trapezoid width uses both bases, permitting narrowing as well as widening.
- Trapezoid bases must be parallel, consistently directed and centred; equal-leg
  oblique parallelograms are rejected. Rectangles are supported.
- Images of differing size are centered in one canvas without resizing.
- Global min/max display normalization is stable over all frames. Raw projection
  values are not normalized; output video is 8-bit, lossy H.264.

## Efficiency

The pixel loop is our algorithm, compiled using Numba nopython mode; the
implementation does not call a third-party plane-slicing routine. Validation
and leg geometry are outside the pixel loop. Runtime per frame is O(H*W), with
O(H*W) output memory. The volume consumes O(sx*sy*sz) memory. Video is streamed.
Actual NRRD loading may temporarily hold both the loaded array and contiguous
copy. Global intensity-range calculation is once per export. JIT specializes
by dtype; first invocation for each dtype includes startup compilation.
