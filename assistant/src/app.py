from numpy import (
    zeros,
    int32,
    frombuffer,
    median,
    linspace,
    array,
    full_like,
    abs,
    concatenate,
)
from sys import argv, exit
from pyaudio import paInt16, PyAudio
from pyqtgraph import PlotWidget, mkPen, mkBrush
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication
from PyQt6.QtCore import QThread, QEventLoop, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QRegion
from widgets.rounded_graph_item import RoundedBarGraphItem

# TODO: Record audio
# TODO: Move to right position
# TODO: scale audio data to circle
# TODO: Start and stop button
# TODO: maybe split in different files


class MicThread(QThread):
    sig = pyqtSignal(bytes)

    def __init__(self, sc):
        super(MicThread, self).__init__()
        self.sc = sc
        self.sig.connect(self.sc.append)
        self.running = True

    def run(self):
        while self.running:
            data = self.sc.stream.read(self.sc.CHUNK)
            self.sig.emit(data)

    def stop(self):
        self.running = False


class StreamController(QWidget):
    def __init__(self):
        super(StreamController, self).__init__()
        self.data = zeros((100000), dtype=int32)
        self.median_data = []
        self.buffer = array([], dtype=int32)
        self.CHUNK = 1024
        self.CHANNELS = 1
        self.RATE = 44100
        self.FORMAT = paInt16
        self.interval_ms = 150
        self.samples_per_interval = int(self.RATE * (self.interval_ms / 1000))

    def setup_stream(self):
        self.audio = PyAudio()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        self.micthread = MicThread(self)
        self.micthread.start()

    def append(self, vals):
        vals = frombuffer(vals, "int16")
        c = self.CHUNK
        self.data[:-c] = self.data[c:]
        self.data[-c:] = vals

        self.buffer = concatenate([self.buffer, vals])

        while len(self.buffer) >= self.samples_per_interval:
            interval_data = self.buffer[: self.samples_per_interval]
            median_value = median(interval_data)
            self.median_data.append(median_value)
            self.buffer = self.buffer[self.samples_per_interval :]

        if len(self.median_data) * self.samples_per_interval > len(self.data):
            self.median_data = self.median_data[
                -len(self.data) // self.samples_per_interval :
            ]

    def breakdown_stream(self):
        self.micthread.terminate()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        loop = QEventLoop()
        QTimer.singleShot(400, loop.quit)
        loop.exec()


class StreamViz(QWidget):
    def __init__(self):
        super(StreamViz, self).__init__()
        self.setWindowTitle("Smart Assistant")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(200, 200)

        self.setCircularShape()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_streamplot)
        self.timer.start(200)

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.p = PlotWidget()
        plot_item = self.p.getPlotItem()
        plot_item.hideAxis("left")
        plot_item.hideAxis("bottom")
        self.p.setBackground(QColor("#009973"))
        self.l.addWidget(self.p)

        self.sc = StreamController()
        self.l.addWidget(self.sc)

        self.bar_color = QColor("#66ff99")
        self.pdataitem = RoundedBarGraphItem(
            x=[],
            height=[],
            width=0.8,
            pen=mkPen(color=self.bar_color, width=2),
            brush=mkBrush(self.bar_color),
            radius=10,
        )
        self.p.addItem(self.pdataitem)
        self.sc.setup_stream()

    def setCircularShape(self):
        size = int(min(self.width(), self.height()) * 0.75)
        x_offset = (self.width() - size) // 2
        y_offset = (self.height() - size) // 2
        region = QRegion(x_offset, y_offset, size, size, QRegion.RegionType.Ellipse)
        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setCircularShape()

    def update_streamplot(self):
        num_bars = len(self.sc.median_data)
        self.x = linspace(-num_bars / 2, num_bars / 2, num_bars)
        heights = array(self.sc.median_data)
        if len(heights) != 0:
            if abs(heights).max() == 0:
                heights = array([0.1] * num_bars)
        y0 = full_like(heights, -heights / 2)
        self.pdataitem.setOpts(
            x=self.x,
            height=heights,
            width=0.8,
            pen=mkPen(color=self.bar_color, width=2),
            brush=mkBrush(self.bar_color),
            y0=y0,
        )
        if len(heights) != 0:
            y_max = abs(heights).max() / 2
            padding = max(y_max * 0.1, 0.1)
            self.p.setYRange(-y_max - padding, y_max + padding)
        self.p.setXRange(-num_bars / 2, num_bars / 2)
        self.p.update()


if __name__ == "__main__":
    app = QApplication(argv)
    s = StreamViz()
    s.show()
    exit(app.exec())
