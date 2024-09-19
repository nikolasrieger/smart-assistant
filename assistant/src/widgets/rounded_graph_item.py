from pyqtgraph import BarGraphItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainterPath


class RoundedBarGraphItem(BarGraphItem):
    def __init__(
        self, x=None, height=None, width=0.8, pen=None, brush=None, y0=None, radius=5
    ):
        super(RoundedBarGraphItem, self).__init__(
            x=x, height=height, width=width, pen=pen, brush=brush, y0=y0
        )
        self.radius = radius

    def paint(self, p, *args):
        p.setPen(self.opts["pen"])
        p.setBrush(self.opts["brush"])
        path = QPainterPath()
        width = self.opts["width"]
        half_width = width / 2

        for i in range(len(self.opts["x"])):
            x = self.opts["x"][i]
            y = self.opts["y0"][i]
            height = self.opts["height"][i]
            bar_width = width

            rect = QRectF(x - half_width, y, bar_width, height)
            path.addRoundedRect(rect, self.radius, self.radius)

        p.drawPath(path)
