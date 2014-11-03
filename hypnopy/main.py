import argparse

from gui import launch_gui
from audio import start_acquisition

def parse_args():
    parser = argparse.ArgumentParser(description='hypnopy: a real-time sound vizualizer')
    parser.add_argument('--freq', nargs=1, type=float, metavar='f', dest='f',
                        help='Test gui with a pure tone of frequency f')
    parser.add_argument('--blobs', nargs=1, type=int, metavar='N', dest='blobs',
                        help='Sets the number of displayed blobs to N (default 100)')
    parser.add_argument('--window', nargs=1, type=int, metavar='N', dest='window',
                        help='Sets the window size used to compute the sound intensity to N (default 8192)')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    p = start_acquisition()
    freq = None if not args.f else args.f[0]
    blobs = 100 if not args.blobs else args.blobs[0]
    launch_gui(blob_count=blobs, freq_test=freq)

