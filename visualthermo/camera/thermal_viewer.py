import matplotlib.pyplot as plt
import numpy as np


class ThermalViewer:
    def __init__(self, camera, recorder):
        self.camera = camera
        self.recorder = recorder
        self.running = True
        self.figure, self.axis = plt.subplots(figsize=(8, 5))
        self.figure.subplots_adjust(top=0.85)
        self.image = self.axis.imshow(
            np.zeros((camera.HEIGHT, camera.WIDTH), dtype=np.uint16),
            cmap='inferno', interpolation='nearest', vmin=0, vmax=1
        )
        self.figure.colorbar(self.image, ax=self.axis, label='Valor Y16')
        self.axis.axis('off')
        self.figure.canvas.mpl_connect('key_press_event', self.on_key)
        self.figure.canvas.mpl_connect('close_event', self.on_close)
        print('Atalhos: S = salvar quadro | R = gravar/parar sequência | Q = sair')

    def on_key(self, event):
        if event.key == 's':
            if hasattr(self, 'last_frame'):
                print(f'Quadro salvo: {self.recorder.save_frame(self.last_frame)}')
        elif event.key == 'r':
            if self.recorder.recording:
                result = self.recorder.stop()
                print(f'Sequência salva: {result[0]} ({result[1]} quadros)' if result else 'Nenhum quadro gravado.')
            else:
                self.recorder.start()
                print('Gravação iniciada.')
        elif event.key == 'q':
            self.running = False
            plt.close(self.figure)

    def on_close(self, _event):
        self.running = False

    def run(self):
        self.camera.start()
        try:
            plt.ion()
            plt.show(block=False)
            while self.running and plt.fignum_exists(self.figure.number):
                frame = self.camera.read_frame()
                if frame is None:
                    print('Fluxo de vídeo encerrado.')
                    break
                self.last_frame = frame
                self.recorder.add_frame(frame)
                minimum = int(frame.min())
                maximum = int(frame.max())
                self.image.set_data(frame)
                self.image.set_clim(minimum, max(maximum, minimum + 1))
                status = ' | GRAVANDO' if self.recorder.recording else ''
                self.axis.set_title(
                    f'FLIR Lepton 3.5 | Min: {minimum} | Max: {maximum}'
                    f' | Média: {frame.mean():.1f}{status}', fontsize=10
                )
                self.figure.canvas.draw_idle()
                plt.pause(0.001)
        except KeyboardInterrupt:
            print('\nInterrompido pelo usuário.')
        finally:
            self.camera.stop()
            if self.recorder.recording:
                result = self.recorder.stop()
                if result:
                    print(f'Sequência salva: {result[0]} ({result[1]} quadros)')
            plt.close(self.figure)