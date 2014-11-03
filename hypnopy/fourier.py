import numpy as np

def make_pure_tone(freq, size, rate):
    t = np.arange(size) * 1./rate
    return np.sin(t * np.pi * 2. * freq)

def sound_power_densities(x, window=np.hanning):
    x = np.array(x, copy=False)
    if len(x.shape) != 1:
        raise TypeError("the frame should be 1-dimensional.")
    n = len(x)
    # Compute a gain alpha that compensates the energy loss caused by the 
    # windowing -- a frame with constant values is used as a reference.
    alpha = 1.0 / np.sqrt(sum(window(n)**2) / n)
    x = alpha * window(n) * x
    xk2 = np.abs(np.fft.rfft(x)) ** 2
    I = xk2 / n ** 2
    return 10*np.log10(I) + 96.
