from collections import deque
from gui import launch_gui

import numpy as np
import pyaudio

# pyaudio acquisition constants
RATE = 44100

BUFFER_SIZE = 2**13 # size of the data on which the DFT operates
BUFFER = deque(np.zeros(BUFFER_SIZE), maxlen=BUFFER_SIZE) # audio data history
CHUNK_SIZE = 2**9 # size of the chunk audio data acquired in one call
                  # 2**9 = about 0.01 s of recording

def callback(in_data, frame_count, time_info, status):
    data = np.fromstring(in_data, np.float32)
    BUFFER.extend(data)
    return (None, pyaudio.paContinue) # When using pyaudio in input-only, the
                                      # callback should return None as first
                                      # element
                  
if __name__ == '__main__':
    # pyaudio initialization
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE,
                    stream_callback=callback)

    launch_gui()

