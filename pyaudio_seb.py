from collections import deque
import re

import pyaudio
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p = pyaudio.PyAudio()


# pyaudio acquisition constants:
RATE = 44100
CHUNK_SIZE = 2**9 # size of the chunk audio data acquired in one call
                  # 2**9 = about 0.01 s of recording

# DFT parameters
WINDOW_SIZE = 2**13 # size of the data on which the DFT operates
WINDOW_OVERLAP = 0.2

BUFFER_SIZE = int(WINDOW_SIZE*(1 + WINDOW_OVERLAP))
BUFFER = deque(np.zeros(BUFFER_SIZE), maxlen=BUFFER_SIZE)

# Global variable storing the data to be displayed
# SPL = Signal Power Level
FOURIER_SPL = []

def callback(in_data, frame_count, time_info, status):
    data = np.fromstring(in_data, np.float32)
    BUFFER.extend(data)
    process_data(data[:WINDOW_SIZE])
    return (None, pyaudio.paContinue)

def process_data(data):
    global FOURIER_SPL
    dft = np.fft.rfft(data*np.hanning(WINDOW_SIZE))
    FOURIER_SPL = sound_power_density(dft)

BASE_FREQUENCIES = {'C':16.35,
                    'C#':17.32, 
                    'D':18.35,
                    'D#':19.45,
                    'E':20.60,
                    'F':21.83,
                    'F#':23.12,
                    'G':24.50,
                    'G#':25.96,
                    'A':27.50,
                    'A#':29.14,
                    'B':30.87}
MIN_FREQ = sorted(BASE_FREQUENCIES.values())[0]

def get_frequency(note, pitch):
    return BASE_FREQUENCIES[note]*2**pitch

def get_closest_note_name(freq):
    i = 0
    while freq > 2*MIN_FREQ:
        freq /= 2.
        i += 1
    return min([(abs(freq - fref), ref_note)
                for ref_note, fref in BASE_FREQUENCIES.items()])[1] + str(i)

def split_note_name(note):
    match = re.match('([A-G]#?)(\d+)$', note)
    return match.group(1), int(match.group(2))

"""Test
for note in BASE_FREQUENCIES.keys():
    note += '0'
    print note
    print split_note_name(note)
"""

def get_polar_coordinates(freq, r_scale=1.):
    """Returns a tuple (r, theta) representing polar coordinates."""
    C0, C1 = [get_frequency('C', pitch) for pitch in (0, 1)]
    _, pitch = split_note_name(get_closest_note_name(freq))
    freq /= 2.**pitch
    theta = (freq - C0)*2*np.pi/(C1 - C0)
    return r_scale*(pitch + theta/(2*np.pi)), theta

def sound_power_density(dft):
    I = np.abs(dft)**2/WINDOW_SIZE**2
    return 10*np.log10(I) + 96.

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=WINDOW_SIZE,
                stream_callback=callback)

p6 = win.addPlot(title="Updating plot")
p6.setAspectLocked()
curve = p6.plot(pen='y')
ptr = 0

MAX_NB_CURVES = 100
CURVES = [QtGui.QGraphicsLineItem() for _ in xrange(MAX_NB_CURVES)]
for c in CURVES:
    p6.addItem(c)
    #c.setZValue(100)
    c.setPen(pg.mkPen('g'))

def draw_spiral(r_max=8., r_scale=1.):
    r = np.linspace(0, r_max, 1000)
    theta = 2*np.pi*r*r_scale
    p6.plot(r*np.cos(theta), r*np.sin(theta), pen='r')
    for note, freq in BASE_FREQUENCIES.items():
        _, theta = get_polar_coordinates(freq)
        p6.plot([0, r_max*np.cos(theta)], [0, r_max*np.sin(theta)], pen='b')

def blob_data(freq, intensity, r_scale=1.):
    r, theta = get_polar_coordinates(freq, r_scale=r_scale)
    blob_length = r_scale*min(1., intensity/50.)
    r_min, r_max = r-blob_length/2., r+blob_length/2.
    return (r_min*np.cos(theta), r_min*np.sin(theta),
            r_max*np.cos(theta), r_max*np.sin(theta))

def update():
    global CURVES
    threshold = 0.
    ranking = sorted([(spl, i) for i, spl in enumerate(FOURIER_SPL)],
                     reverse=True)[:MAX_NB_CURVES]
    frequencies = np.fft.rfftfreq(WINDOW_SIZE, 1./RATE)
    for j, el in enumerate(ranking):
        spl, i = el
        if spl > threshold:
            freq = frequencies[i]
            blob = blob_data(freq, spl)
            CURVES[j].setLine(*blob)
        else:
            CURVES[j].setLine(0, 0, 0, 0)

draw_spiral()

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)
QtGui.QApplication.instance().exec_()
