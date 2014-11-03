import argparse

from gui import launch_gui
from audio import start_acquisition

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='hypnopy: a real-time sound vizualizer')
    parser.add_argument('--freq', nargs=1, type=float, metavar='f', dest='f',
                        help='Test gui with a pure tone of frequency f')
    args = parser.parse_args()
    p = start_acquisition()
    freq = None if not args.f else args.f[0]
    launch_gui(freq_test=freq)

