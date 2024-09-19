from numpy import (
    linspace,
    array,
    full_like,
    abs,
)
from sys import argv, exit
from pyqtgraph import PlotWidget, mkPen, mkBrush
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QRegion
from widgets.rounded_graph_item import RoundedBarGraphItem
from engine.audio_engine.stream_controller import StreamController

# TODO: Record audio
# TODO: Move to right position
# TODO: scale audio data to circle
# TODO: Start and stop button


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
