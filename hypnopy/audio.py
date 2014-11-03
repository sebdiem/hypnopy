from collections import deque
import numpy as np

import pyaudio

# pyaudio acquisition constants
RATE = 44100
_CHUNK_SIZE = 2**9 # size of the chunk audio data acquired in one call
                  # 2**9 = about 0.01 s of recording

_BUFFER_SIZE = 2**13 # max size of the data on which the DFT operates
_BUFFER = deque(np.zeros(_BUFFER_SIZE), maxlen=_BUFFER_SIZE) # audio data history

def callback(in_data, frame_count, time_info, status):
    data = np.fromstring(in_data, np.float32)
    _BUFFER.extend(data)
    return (None, pyaudio.paContinue) # When using pyaudio in input-only, the
                                      # callback should return None as first
                                      # element

def get_buffer():
    return _BUFFER

def start_acquisition():
    # pyaudio initialization
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=_CHUNK_SIZE,
                    stream_callback=callback)
    return p
