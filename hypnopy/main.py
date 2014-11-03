from gui import launch_gui
from audio import start_acquisition

if __name__ == '__main__':
    p = start_acquisition()
    launch_gui()

