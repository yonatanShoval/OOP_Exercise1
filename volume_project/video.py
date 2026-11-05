"""Display normalization and constant-size streaming MP4 export."""
import numpy as np
import imageio.v2 as imageio
import sys
from PIL import Image, ImageDraw, ImageFont
from .model import InvalidPlane


class GrayMapper:
    def __init__(self, data):
        self.low = float(data.min())
        self.high = float(data.max())

    def convert(self, image):
        if self.high == self.low:
            return np.zeros(image.shape, dtype=np.uint8)
        scaled = (image.astype(np.float64) - self.low) * (255.0 / (self.high-self.low))
        return np.clip(scaled, 0, 255).astype(np.uint8)
    
class ErrorFrame:
    """A black frame with a white X and text naming the invalid CSV line."""

    def __init__(self, invalid_plane):
        self.invalid_plane = invalid_plane

    def draw(self, height, width):
        image = Image.new('L', (width, height), 0)
        pen = ImageDraw.Draw(image)
        pen.line([(0, 0), (width - 1, height - 1)], fill=255)
        pen.line([(width - 1, 0), (0, height - 1)], fill=255)
        size = max(8, width // 12)
        try:
            font = ImageFont.load_default(size=size)
        except TypeError:
            font = ImageFont.load_default()
        text = f'INVALID PLANE\nCSV line {self.invalid_plane.line}'
        box = pen.multiline_textbbox((0, 0), text, font=font, align='center')
        x = (width - (box[2] - box[0])) // 2
        y = (height - (box[3] - box[1])) // 2
        pen.rectangle([x - 4, y - 4, x + box[2] - box[0] + 4, y + box[3] - box[1] + 4], fill=0)
        pen.multiline_text((x, y), text, fill=255, font=font, align='center')
        return np.asarray(image, dtype=np.uint8)
        

class VideoExporter:
    def __init__(self, fps=30):
        if not np.isfinite(fps) or fps <= 0:
            raise ValueError('FPS must be finite and positive')
        self.fps = fps

    def write(self, path, volume, planes, projector):
        # H.264 yuv420p requires even dimensions. No per-frame rescaling.
        sizes = [p.shape for p in planes if not isinstance(p, InvalidPlane)]
        height = max((h for h, w in sizes), default=64)
        width = max((w for h, w in sizes), default=64)
        if height > projector.max_side or width > projector.max_side:
            raise ValueError('Video canvas exceeds projection size limit')
        height += height % 2
        width += width % 2
        mapper = GrayMapper(volume.data)
        with imageio.get_writer(str(path), format='FFMPEG', fps=self.fps,
                               codec='libx264', macro_block_size=1,
                               pixelformat='yuv420p') as writer:
            for plane in planes:
                if isinstance(plane, InvalidPlane):
                    print(
                        f'CSV line {plane.line}: {plane.message}',
                        file=sys.stderr
                    )
                    frame = ErrorFrame(plane).draw(height, width)
                    writer.append_data(frame)
                    continue
                image = mapper.convert(projector.project(volume, plane))
                frame = np.zeros((height, width), dtype=np.uint8)
                h, w = image.shape
                y, x = (height-h)//2, (width-w)//2
                frame[y:y+h, x:x+w] = image
                writer.append_data(frame)
        return len(planes), width, height
