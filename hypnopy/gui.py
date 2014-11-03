import numpy as np

from audio import RATE, get_buffer
from fourier import sound_power_densities
from note_utils import BASE_FREQUENCIES, get_base_frequency_and_power_of_two, get_frequency

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

_SPL_THRESHOLD = 0. # we do not display frequencies whose SPL is below this limit
def _update_SPL_threshold(i):
    global _SPL_THRESHOLD
    _SPL_THRESHOLD = i

def get_polar_coordinates(freq, r_scale=1.):
    """Returns a tuple (r, theta) representing polar coordinates of a frequency `freq`.
    The twelve notes of the Pythagorician scale can be displayed on a 2D spiral, with
    differences in angles proportional to the differences in frequencies.
    Higher octaves of a fundamental note N are represented with the same angle theta and a
    radius increased by the difference in octaves."""
    C0, C1 = [get_frequency('C', oc) for oc in (0, 1)] # the spiral starts at C0
    freq, octave = get_base_frequency_and_power_of_two(freq)
    theta = (freq - C0)*2*np.pi/(C1 - C0)
    return r_scale*(octave + theta/(2*np.pi)), theta

def draw_legend(plot_widget, freq_max=20000., r_scale=1., color=(128, 64, 64)):
    r_max = np.log2(freq_max/BASE_FREQUENCIES['C']) * r_scale
    for note, freq in BASE_FREQUENCIES.items():
        _, theta = get_polar_coordinates(freq)
        plot_widget.plot([0, r_max*np.cos(theta)], 
                         [0, r_max*np.sin(theta)],
                         pen=pg.mkPen(color=color, style=QtCore.Qt.DotLine))
        text = pg.TextItem(note, anchor=(0.5, 0.5))
        text.setPos((r_max + 1.)*np.cos(theta), (r_max + 1.)*np.sin(theta))
        plot_widget.addItem(text)

def draw_spiral(plot_widget, freq_max=20000., r_scale=1., color=(128, 64, 64)):
    r_max = np.log2(freq_max/BASE_FREQUENCIES['C']) * r_scale
    r = np.linspace(0, r_max, 1000)
    theta = 2 * np.pi * r
    plot_widget.plot(r*np.cos(theta), r*np.sin(theta), pen=pg.mkPen(color=color))
    draw_legend(plot_widget, freq_max, r_scale, color)

    graphLim = 0.5 * (r_max * 2.2)
    plot_widget.getPlotItem().setRange(xRange=(-graphLim, graphLim),
                                       yRange=(-graphLim, graphLim))

def blob_coordinates(freq, intensity, min_intensity, max_intensity, r_scale=1.):
    r, theta = get_polar_coordinates(freq, r_scale=r_scale)
    intensity_diff = max(0, intensity - min_intensity)
    blob_length = r_scale * min(1., intensity_diff / (max_intensity - min_intensity))
    r_min, r_max = r - blob_length / 2., r + blob_length / 2.
    return (r_min*np.cos(theta), r_min*np.sin(theta),
            r_max*np.cos(theta), r_max*np.sin(theta))

def update(CURVES):
    global _SPL_THRESHOLD, SAVE
    BUFFER = get_buffer()
    #import numpy as np
    #t = np.arange(len(BUFFER)) * 1./44100
    #BUFFER = np.sin(t * np.pi * 2. * 8150.)
    FOURIER_SPL = sound_power_densities(BUFFER)
    ranking = sorted([(spl, i) for i, spl in enumerate(FOURIER_SPL)],
                     reverse=True)[:len(CURVES)]
    frequencies = np.fft.rfftfreq(len(BUFFER), 1./RATE)
    for j, el in enumerate(ranking):
        spl, i = el
        if spl > _SPL_THRESHOLD:
            freq = frequencies[i]
            blob = blob_coordinates(freq, spl, min_intensity=_SPL_THRESHOLD, max_intensity=96.)
            CURVES[j].setLine(*blob)
        else:
            CURVES[j].setLine(0, 0, 0, 0)

def create_slider_widget(label, unit, min_value, max_value, init_value, step,
                         connect, max_width):
    """Creates a widget composed of a vertical layout with:
    - a label describing the quantity being changed by the slider
    - a label showing the current value of the quantity
    - a horizontal slider enabling to change the quantity.
      `connect` is used to update the quantity"""
    class IntLabel(QtGui.QLabel):
        def setValue(self, i):
            self.setText('%d %s' % (i, unit))
    slider = QtGui.QSlider(orientation=QtCore.Qt.Horizontal)
    slider.setMinimum(min_value)
    slider.setMaximum(max_value)
    slider.setSingleStep(step)
    slider.setValue(init_value)

    spinbox = IntLabel()
    spinbox.setValue(init_value)

    slider.valueChanged.connect(spinbox.setValue)
    slider.valueChanged.connect(connect)

    verticalLayout = QtGui.QVBoxLayout()
    verticalLayout.addWidget(QtGui.QLabel(label))
    verticalLayout.addWidget(spinbox)
    verticalLayout.setAlignment(spinbox, QtCore.Qt.AlignHCenter)
    verticalLayout.addWidget(slider)

    slider_widget = QtGui.QWidget()
    slider_widget.setLayout(verticalLayout)
    slider_widget.setMaximumHeight(100)
    slider_widget.setMaximumWidth(max_width)

    return slider_widget

def create_plot_widget(name):
    plot = pg.PlotWidget(name=name)
    plot.hideAxis('left')
    plot.hideAxis('bottom')
    plot.setAspectLocked()
    return plot

def create_window():
    win = QtGui.QMainWindow()
    win.resize(1000,600)
    win.setWindowTitle('HypnoPy')

    pg.setConfigOptions(antialias=True) # Enable antialiasing for prettier plots

    plot_widget = create_plot_widget('Spiral')
    slider_widget = create_slider_widget(label='SPL threshold:',
                                         unit='dB',
                                         min_value=-50,
                                         max_value=50,
                                         init_value=0,
                                         step=1,
                                         connect=_update_SPL_threshold,
                                         max_width=200)
    layout = pg.LayoutWidget()
    layout.addWidget(plot_widget)
    layout.addWidget(slider_widget)
    layout.show()
    return layout, plot_widget

def launch_gui():
    # pyqtgraph initialization
    app = QtGui.QApplication([])
    layout, plot_widget = create_window()

    MAX_NB_CURVES = 100
    CURVES = [QtGui.QGraphicsLineItem() for _ in xrange(MAX_NB_CURVES)]
    for c in CURVES:
        plot_widget.addItem(c)
        c.setPen(pg.mkPen(color=(255, 255, 128)))
    draw_spiral(plot_widget)

    timer = QtCore.QTimer()
    timer.timeout.connect(lambda : update(CURVES))
    timer.start(20)

    QtGui.QApplication.instance().exec_()
