from nose.tools import *
from numpy.testing import assert_array_almost_equal as assert_almost_equal
import numpy as np
from hypnopy.fourier import *


def test_get_closest_not_name():
    assert get_closest_note_name(16.35) == 'C0'
    assert get_closest_note_name(2**8*16.35) == 'C8'
    assert get_closest_note_name(2**1*27.) == 'A1'
    assert get_closest_note_name(2**7*32.) == 'C8'

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

def make_pure_sinusoid(freq, dt, size=1000):
    t = np.arange(8000) * dt
    return np.sin(t * 2 * np.pi * freq)

def test_sound_power_densities():
    sig = make_pure_sinusoid(8000, 1./44100)
    I =  sound_power_densities(sig)
    from matplotlib import pyplot as plt
    plt.plot(np.fft.rfftfreq(1000, 1./44100), I)
    plt.show()
    assert_almost_equal(sound_power_densities(np.ones(100), np.ones)[0], 96.)
    assert_almost_equal(sound_power_densities(np.ones(100), np.hanning)[0], 96.)
