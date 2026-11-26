from pathlib import Path

from visualthermo.camera.lepton_camera import LeptonCamera
from visualthermo.camera.thermal_recorder import ThermalRecorder
from visualthermo.camera.thermal_viewer import ThermalViewer


def main():
    project_root = Path(__file__).resolve().parent

    camera = LeptonCamera('/dev/video2')
    recorder = ThermalRecorder(project_root / 'data' / 'captures')
    viewer = ThermalViewer(camera, recorder)

    viewer.run()


if __name__ == '__main__':
    main()