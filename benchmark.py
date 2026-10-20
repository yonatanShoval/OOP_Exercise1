"""Measure projection separately from I/O, JIT and MP4 encoding."""
import json
import platform
from pathlib import Path
import time
import numpy as np
from volume_project.model import Volume, Plane
from volume_project.projector import Projector


def main():
    volume=Volume(np.full((500,500,500),127,dtype=np.uint8),{})
    projector=Projector()
    cases={
        'axis_rectangle':Plane(((0,0,250),(499,0,250),(0,499,250),(499,499,250))),
        'oblique_rectangle':Plane(((50,0,50),(449,0,449),(50,499,50),(449,499,449))),
        'triangle':Plane(((249.5,0,250),(0,499,250),(499,499,250)))
    }
    report={'python':platform.python_version(),'platform':platform.platform(),
            'processor':platform.processor(),'volume_shape':[500]*3,
            'volume_bytes':volume.data.nbytes,'method':'100 timed frames per run, 5 runs; JIT warmup excluded; no I/O or encoding',
            'cases':{}}
    for name,plane in cases.items():
        projector.project(volume,plane)
        rates=[]
        for _ in range(5):
            start=time.perf_counter()
            for i in range(100): projector.project(volume,plane)
            rates.append(100/(time.perf_counter()-start))
        report['cases'][name]={'shape':list(plane.shape),'fps_runs':rates,
                               'median_fps':float(np.median(rates)),'minimum_fps':min(rates)}
    path=Path(__file__).resolve().parent/'results'/'benchmark.json'
    path.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
