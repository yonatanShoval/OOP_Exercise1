"""Usage: python Ex0.py file.nrrd file.csv file.mp4"""
import argparse
from pathlib import Path
import sys
from volume_project.model import Volume, read_planes
from volume_project.projector import Projector
from volume_project.video import VideoExporter


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sample NRRD planes and create an MP4.')
    parser.add_argument('volume', type=Path)
    parser.add_argument('planes', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--fps', type=float, default=30)
    args = parser.parse_args(argv)
    try:
        if args.output.suffix.lower() != '.mp4':
            raise ValueError('Output must have an .mp4 extension')
        if args.output.resolve() in (args.volume.resolve(), args.planes.resolve()):
            raise ValueError('Output must differ from both input files')
        
        volume = Volume.load(args.volume)
        planes = read_planes(args.planes, allow_invalid=True)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        frames, width, height = VideoExporter(args.fps).write(args.output, volume, planes, Projector())
        print(f'Volume {volume.data.shape}; wrote {frames} frames ({width}x{height}) to {args.output}')
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
