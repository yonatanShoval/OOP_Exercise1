"""Display normalization and constant-size streaming MP4 export."""
import numpy as np
import imageio.v2 as imageio


class GrayMapper:
    def __init__(self, data):
        self.low = float(data.min())
        self.high = float(data.max())

    def convert(self, image):
        if self.high == self.low:
            return np.zeros(image.shape, dtype=np.uint8)
        scaled = (image.astype(np.float64) - self.low) * (255.0 / (self.high-self.low))
        return np.clip(scaled, 0, 255).astype(np.uint8)


class VideoExporter:
    def __init__(self, fps=30):
        if not np.isfinite(fps) or fps <= 0:
            raise ValueError('FPS must be finite and positive')
        self.fps = fps

    def write(self, path, volume, planes, projector):
        # H.264 yuv420p requires even dimensions. No per-frame rescaling.
        sizes = [p.shape for p in planes]
        height = max(h for h, w in sizes)
        width = max(w for h, w in sizes)
        if height > projector.max_side or width > projector.max_side:
            raise ValueError('Video canvas exceeds projection size limit')
        height += height % 2
        width += width % 2
        mapper = GrayMapper(volume.data)
        with imageio.get_writer(str(path), format='FFMPEG', fps=self.fps,
                               codec='libx264', macro_block_size=1,
                               pixelformat='yuv420p') as writer:
            for plane in planes:
                image = mapper.convert(projector.project(volume, plane))
                frame = np.zeros((height, width), dtype=np.uint8)
                h, w = image.shape
                y, x = (height-h)//2, (width-w)//2
                frame[y:y+h, x:x+w] = image
                writer.append_data(frame)
        return len(planes), width, height
