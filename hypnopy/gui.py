import numpy as np

from fourier import BASE_FREQUENCIES, get_polar_coordinates, process_data

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

def test(i):
    global SPL_THRESHOLD
    SPL_THRESHOLD = i

class IntLabel(QtGui.QLabel):
    def setValue(self, i):
        self.setText('%d dB' % i)
    

def draw_spiral(p6, freq_max=20000., r_scale=1.):
    r_max = np.log2(freq_max/BASE_FREQUENCIES['C'])
    r = np.linspace(0, r_max, 1000)
    theta = 2*np.pi*r*r_scale
    p6.plot(r*np.cos(theta), r*np.sin(theta), pen=pg.mkPen(color=(128, 64, 64)))
    for note, freq in BASE_FREQUENCIES.items():
        _, theta = get_polar_coordinates(freq)
        p6.plot([0, r_max*np.cos(theta)], [0, r_max*np.sin(theta)],
                pen=pg.mkPen(color=(128, 64, 64), style=QtCore.Qt.DotLine))
        text = pg.TextItem(note, anchor=(0.5, 0.5))
        text.setPos((r_max + 1.)*np.cos(theta), (r_max + 1.)*np.sin(theta))
        p6.addItem(text)

def blob_data(freq, intensity, r_scale=1.):
    r, theta = get_polar_coordinates(freq, r_scale=r_scale)
    blob_length = r_scale*min(1., intensity/50.)
    r_min, r_max = r-blob_length/2., r+blob_length/2.
    return (r_min*np.cos(theta), r_min*np.sin(theta),
            r_max*np.cos(theta), r_max*np.sin(theta))

def update():
    global CURVES, SPL_THRESHOLD
    process_data(BUFFER)
    ranking = sorted([(spl, i) for i, spl in enumerate(FOURIER_SPL)],
                     reverse=True)[:MAX_NB_CURVES]
    frequencies = np.fft.rfftfreq(WINDOW_SIZE, 1./RATE)
    for j, el in enumerate(ranking):
        spl, i = el
        if spl > SPL_THRESHOLD:
            freq = frequencies[i]
            blob = blob_data(freq, spl)
            CURVES[j].setLine(*blob)
        else:
            CURVES[j].setLine(0, 0, 0, 0)

def launch_gui():
    # pyqtgraph initialization
    app = QtGui.QApplication([])

    win = QtGui.QMainWindow()
    win.resize(1000,600)
    win.setWindowTitle('pyqtgraph example: Plotting')

    pg.setConfigOptions(antialias=True) # Enable antialiasing for prettier plots

    lw = pg.LayoutWidget()
    p6 = pg.PlotWidget(name="Spiral")
    lw.addWidget(p6)
    sidebar = QtGui.QWidget()
    verticalLayout = QtGui.QVBoxLayout()
    sidebar.setLayout(verticalLayout)
    sidebar.setMaximumHeight(100)
    sidebar.setMaximumWidth(200)
    slider = QtGui.QSlider(orientation=QtCore.Qt.Horizontal)
    slider.valueChanged.connect(test)
    slider.setMinimum(-50)
    slider.setMaximum(50)
    slider.setSingleStep(1)
    lab = QtGui.QLabel("SPL threshold:")
    spinbox = IntLabel('0 dB')
    slider.valueChanged.connect(spinbox.setValue)
    verticalLayout.addWidget(lab)
    verticalLayout.addWidget(spinbox)
    verticalLayout.setAlignment(spinbox, QtCore.Qt.AlignHCenter)
    verticalLayout.addWidget(slider)

    lw.addWidget(sidebar)
    #p6 = win.addPlot(title="Updating plot")
    p6.setAspectLocked()
    ptr = 0

    MAX_NB_CURVES = 100
    CURVES = [QtGui.QGraphicsLineItem() for _ in xrange(MAX_NB_CURVES)]
    for c in CURVES:
        p6.addItem(c)
        c.setPen(pg.mkPen(color=(255, 255, 128)))
    draw_spiral(p6)
    lw.show()

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(20)

    QtGui.QApplication.instance().exec_()
