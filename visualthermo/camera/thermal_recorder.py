from datetime import datetime
from pathlib import Path
import json
import numpy as np


class ThermalRecorder:
    def __init__(self, output_dir='capturas'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.frames = []
        self.timestamps = []
        self.recording = False

    def save_frame(self, frame):
        path = self.output_dir / f'quadro_{datetime.now():%Y%m%d_%H%M%S_%f}.npy'
        np.save(path, frame)
        return path

    def start(self):
        self.frames = []
        self.timestamps = []
        self.recording = True

    def add_frame(self, frame):
        if self.recording:
            self.frames.append(frame.copy())
            self.timestamps.append(datetime.now().astimezone().isoformat())

    def stop(self):
        if not self.recording:
            return None
        self.recording = False
        if not self.frames:
            return None
        stem = f'sequencia_{datetime.now():%Y%m%d_%H%M%S_%f}'
        path = self.output_dir / f'{stem}.npz'
        frames = np.stack(self.frames, axis=0)
        np.savez_compressed(path, frames=frames,
                            timestamps=np.asarray(self.timestamps))
        metadata = {
            'format': 'Y16', 'shape': list(frames.shape),
            'dtype': str(frames.dtype),
            'note': 'Valores Y16 não convertidos para temperatura.'
        }
        (self.output_dir / f'{stem}.json').write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        count = len(self.frames)
        self.frames = []
        self.timestamps = []
        return path, count