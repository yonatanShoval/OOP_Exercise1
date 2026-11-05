import csv
from pathlib import Path
import tempfile
import unittest
import numpy as np
import nrrd
import imageio.v2 as imageio
from volume_project.model import Volume, Plane, InvalidPlane, read_planes
from volume_project.projector import Projector
from volume_project.video import GrayMapper, VideoExporter, ErrorFrame
from Ex0 import main


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        x,y,z = np.indices((12,12,12))
        self.volume = Volume((x+20*y+400*z).astype(np.uint32), {})
        self.projector = Projector()

    def test_axis_rectangle_exact(self):
        p=Plane(((2,1,3),(6,1,3),(2,5,3),(6,5,3)))
        got=self.projector.project(self.volume,p)
        expected=np.array([[x+20*y+400*3 for x in range(2,7)] for y in range(2,6)],dtype=np.uint32)
        np.testing.assert_array_equal(got,expected)

    def test_oblique_exact(self):
        # Across one row, both x and z grow; this cannot be an axis-only extraction.
        p=Plane(((1,1,1),(4,1,5),(1,5,1),(4,5,5)))
        got=self.projector.project(self.volume,p)
        expected=[]
        for y in range(2,6):
            expected.append([int(np.floor(1+.6*s+.5))+20*y+400*int(np.floor(1+.8*s+.5)) for s in range(6)])
        np.testing.assert_array_equal(got,np.array(expected,dtype=np.uint32))

    def test_triangle_mask_and_base(self):
        vol=Volume(np.ones((12,12,12),dtype=np.uint8)*9,{})
        p=Plane(((5,1,3),(2,5,3),(8,5,3)))
        got=self.projector.project(vol,p)
        self.assertEqual(got.shape,(5,7))
        np.testing.assert_array_equal(got[-1],np.full(7,9))
        self.assertTrue(np.any(got[0]==0))

    def test_trapezoid(self):
        p=Plane(((4,1,3),(6,1,3),(1,5,3),(9,5,3)))
        got=self.projector.project(self.volume,p)
        np.testing.assert_array_equal(got[-1],self.volume.data[1:10,5,3])

    def test_outside_and_rounding(self):
        p=Plane(((-2,1,3),(2,1,3),(-2,3,3),(2,3,3)))
        got=self.projector.project(self.volume,p)
        self.assertTrue(np.all(got[:,:2]==0))
        self.assertEqual(got[0,2],self.volume.data[0,2,3])
        p=Plane(((1.5,1,3),(3.5,1,3),(1.5,3,3),(3.5,3,3)))
        self.assertEqual(self.projector.project(self.volume,p)[0,0],self.volume.data[2,2,3])
        # Less than half a voxel outside still rounds to the edge voxel.
        p=Plane(((-0.3,1,3),(2.7,1,3),(-0.3,3,3),(2.7,3,3)))
        self.assertEqual(self.projector.project(self.volume,p)[0,0],self.volume.data[0,2,3])
        # The far edge: 11.4 rounds to 11 (inside), 11.6 rounds to 12 (outside).
        p=Plane(((11.4,1,3),(11.4,3,1),(11.4,3,5)))
        self.assertEqual(self.projector.project(self.volume,p)[-1,2],self.volume.data[11,3,3])
        p=Plane(((11.6,1,3),(11.6,3,1),(11.6,3,5)))
        self.assertTrue(np.all(self.projector.project(self.volume,p)==0))

    def test_integer_types(self):
        p=Plane(((1,1,1),(4,1,1),(1,4,1),(4,4,1)))
        for dtype in (np.uint8,np.uint16,np.uint32,np.int16):
            vol=Volume(np.full((6,6,6),np.iinfo(dtype).max,dtype=dtype),{})
            out=self.projector.project(vol,p)
            self.assertEqual(out.dtype,dtype)
            self.assertTrue(np.all(out==np.iinfo(dtype).max))

    def test_invalid_geometry(self):
        for points in [((0,0,0),)*3, ((0,0,0),(1,0,0),(2,0,0)),
                       ((0,0,0),(1,0,0),(0,2,0)),
                       ((0,0,0),(2,0,0),(1,2,0),(3,2,0)),
                       ((0,0,0),(10,0,0),(3,4,0),(7,4,0)),
                       ((float('nan'),0,0),(1,0,0),(0,1,0))]:
            with self.assertRaises(ValueError): Plane(points)

    def test_invalid_volume_and_size(self):
        for data in (np.zeros((3,3)),np.zeros((3,3,3),dtype=float),np.zeros((0,3,3),dtype=np.uint8)):
            with self.assertRaises(ValueError): Volume(data,{})
        with self.assertRaises(ValueError):
            Projector(max_side=2).project(self.volume,Plane(((1,1,1),(4,1,1),(1,4,1),(4,4,1))))

    def test_csv_line_errors(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'planes.csv'
            p.write_text('# comment\n\n1,2,3\n')
            with self.assertRaisesRegex(ValueError,'line 3'): read_planes(p)
            p.write_text('')
            with self.assertRaisesRegex(ValueError,'no planes'): read_planes(p)

    def test_mapper(self):
        data=np.array([-20,0,20],dtype=np.int16)
        np.testing.assert_array_equal(GrayMapper(data).convert(data),[0,127,255])
        np.testing.assert_array_equal(GrayMapper(np.ones(3)).convert(np.ones(3)),[0,0,0])

    def test_error_frame(self):
        frame = ErrorFrame(InvalidPlane(7, 'unequal legs')).draw(120, 200)
        self.assertEqual(frame.shape, (120, 200))
        self.assertEqual(frame.dtype, np.uint8)
        self.assertTrue(frame.max() == 255 and frame.min() == 0)

    def test_nrrd_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'tiny.nrrd'
            nrrd.write(str(path),self.volume.data,index_order='F')
            np.testing.assert_array_equal(Volume.load(path).data,self.volume.data)

    def test_end_to_end_and_frame_order(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); src=root/'data.nrrd'; csv_path=root/'p.csv'; out=root/'movie.mp4'
            nrrd.write(str(src),self.volume.data,index_order='F')
            # Constant-z planes become progressively lighter under global normalization.
            with csv_path.open('w',newline='') as f:
                w=csv.writer(f)
                for z in (1,5,9):
                    w.writerow([1,1,z,9,1,z,1,9,z,9,9,z])
            self.assertEqual(main([str(src),str(csv_path),str(out)]),0)
            with imageio.get_reader(str(out)) as reader:
                frames=list(reader.iter_data())
            self.assertEqual(len(frames),3)
            self.assertEqual(frames[0].shape[:2],(8,10))
            means=[f.mean() for f in frames]
            self.assertTrue(means[0]<means[1]<means[2])
            # Running the same command again overwrites the video.
            self.assertEqual(main([str(src),str(csv_path),str(out)]),0)


if __name__=='__main__': unittest.main()
