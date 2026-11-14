import subprocess
import numpy as np


class LeptonCamera:
    WIDTH = 160
    HEIGHT = 120
    FRAME_BYTES = WIDTH * HEIGHT * 2

    def __init__(self, device='/dev/video2'):
        self.device = device
        self.process = None

    def start(self):
        if self.process is not None:
            raise RuntimeError('A câmera já está iniciada.')
        command = [
            'v4l2-ctl', '-d', self.device,
            '--set-fmt-video=width=160,height=120,pixelformat=Y16 ',
            '--stream-mmap', '--stream-count=0', '--stream-to=-'
        ]
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            bufsize=0
        )

    def read_frame(self):
        if self.process is None:
            raise RuntimeError('Inicie a câmera antes de ler quadros.')
        data = bytearray()
        while len(data) < self.FRAME_BYTES:
            chunk = self.process.stdout.read(self.FRAME_BYTES - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return np.frombuffer(data, dtype='<u2').reshape(self.HEIGHT, self.WIDTH).copy()

    def stop(self):
        if self.process is None:
            return
        process = self.process
        self.process = None
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if process.stdout is not None:
            process.stdout.close()