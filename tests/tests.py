from nose.tools import *
from numpy.testing import assert_array_almost_equal as assert_almost_equal
import numpy as np

from hypnopy.note_utils import BASE_FREQUENCIES, get_closest_note, split_note_name, get_frequency
from hypnopy.gui import get_polar_coordinates
from hypnopy.fourier import sound_power_densities

def test_get_frequency():
    assert get_frequency('C', 0) == 16.35
    assert get_frequency('C', 1) == 32.7

def test_get_closest_note():
    assert get_closest_note(16.35) == ('C', 0)
    assert get_closest_note(2**8*16.35) == ('C', 8)
    assert get_closest_note(2**1*27.) == ('A', 1)
    assert get_closest_note(2**7*32.) == ('C', 8)

def test_split_note_name():
    assert split_note_name('C0') == ('C', 0)
    assert split_note_name('F#0') == ('F#', 0)
    assert split_note_name('B#10') == ('B#', 10)

def test_get_polar_coordinates():
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['C']*2, r_scale=1.)
    assert (r, theta) == (1., 0.)
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['C']*2, r_scale=10.)
    assert (r, theta) == (10., 0.)
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['C#']*2, r_scale=10.)
    assert_almost_equal(theta, 0.3727638989580545)
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['D']*2, r_scale=10.)
    assert_almost_equal(theta, 0.7685853586764019)
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['D#']*2, r_scale=10.)
    assert_almost_equal(theta, 1.191307305948422)
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['E']*2, r_scale=10.)
    assert_almost_equal(theta, 1.6332438871873542)
    r, theta = get_polar_coordinates(BASE_FREQUENCIES['B']*2, r_scale=10.)
    assert_almost_equal(theta, 5.579929703990677)
    r, theta = get_polar_coordinates(8135, r_scale=10.)
    assert_almost_equal(theta, 5.928615264758949)

def make_pure_sinusoid(freq, dt, size=1000):
    t = np.arange(8000) * dt
    return np.sin(t * 2 * np.pi * freq)

def pure_sinusoid_t(freq, rate=44100.):
    sig = make_pure_sinusoid(freq, 1./rate)
    I = sound_power_densities(sig, np.hanning)
    df = np.fft.rfftfreq(len(sig), 1./rate)[1]
    i = int(freq/df)
    assert I[i] > 80
    assert (I[:i-25] < 0).all()
    assert (I[i+25:] < 0).all()

def test_sound_power_densities():
    assert_almost_equal(sound_power_densities(np.ones(100), np.ones)[0], 96.)

def test_pure_sinusoids_power_densities():
    for freq in (800, 4000, 10000, 16000):
        print freq
        pure_sinusoid_t(freq)
