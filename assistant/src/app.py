from numpy import linspace, array, full_like, abs
from sys import argv, exit
from pyqtgraph import PlotWidget, mkPen, mkBrush
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QApplication, QLabel, QStackedLayout
from PyQt6.QtCore import QTimer, Qt, QRectF, QSize
from PyQt6.QtGui import QColor, QRegion, QPainterPath, QPainter, QBrush, QPen, QPixmap
from engine.audio_engine.stream_controller import StreamController
from widgets.rounded_graph_item import RoundedBarGraphItem
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel
from dotenv import load_dotenv
from os import getenv 


class StreamViz(QWidget):
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        super(StreamViz, self).__init__()
        self.setWindowTitle("Smart Assistant")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent")

        self.setFixedSize(150, 150)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_streamplot)

        self.is_playing = False

        self.main_widget = QWidget()

        self.l = QVBoxLayout()
        self.main_widget.setLayout(self.l)
        self.main_widget.setStyleSheet("background: transparent")

        self.p = PlotWidget()
        plot_item = self.p.getPlotItem()
        plot_item.hideAxis("left")
        plot_item.hideAxis("bottom")
        self.p.setBackground(None)
        self.setStyleSheet("background: transparent")
        self.l.addWidget(self.p)

        self.sc = StreamController(model, embedding_model)
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

        self.image = QLabel(self)
        self.image.setPixmap(
            QPixmap("icons/mic_icon.png").scaled(
                QSize(100, 100),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.image)
        self.stacked_layout.addWidget(self.main_widget)
        self.setLayout(self.stacked_layout)
        self.sc.breakdown_stream()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        brush = QBrush(QColor("#009973"))
        pen = QPen(QColor("#009973"))

        painter.setBrush(brush)
        painter.setPen(pen)

        rect = QRectF(1, 1, self.width() - 1, self.height() - 1)
        painter.drawEllipse(rect)

        path = QPainterPath()
        path.addEllipse(rect)
        painter.setClipPath(path)

    def setCircularShape(self):
        size = int(min(self.width(), self.height()) * 0.75)
        x_offset = (self.width() - size) // 2
        y_offset = (self.height() - size) // 2
        rect = QRectF(x_offset, y_offset, size, size)

        path = QPainterPath()
        path.addEllipse(rect)

        region = QRegion(path.toFillPolygon().toPolygon())

        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(1, self.lowerRight)
        self.show()

    def lowerRight(self):
        screen_geom = QApplication.primaryScreen().availableGeometry()
        pos = screen_geom.bottomRight() - self.rect().bottomRight()
        self.move(pos)

    def update_streamplot(self):
        num_bars = len(self.sc.median_data)
        self.x = linspace(-num_bars / 2, num_bars / 2, num_bars)
        self.x = self.x * (0.8 + 1)
        heights = array(self.sc.median_data)
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

    def mousePressEvent(self, _):
        if self.is_playing:
            self.sc.breakdown_stream()
            self.timer.stop()
            self.p.hide()
            self.image.show()
            self.stacked_layout.removeWidget(self.main_widget)
            self.stacked_layout.removeWidget(self.image)
            self.stacked_layout.addWidget(self.image)
            self.stacked_layout.addWidget(self.main_widget)
        else:
            self.sc.restore_stream()
            self.timer.start(200)
            self.p.setBackground(None)
            self.setStyleSheet("background: transparent")
            self.p.show()
            self.image.hide()
            self.stacked_layout.removeWidget(self.main_widget)
            self.stacked_layout.removeWidget(self.image)
            self.stacked_layout.addWidget(self.main_widget)
            self.stacked_layout.addWidget(self.image)
        self.is_playing = not self.is_playing


if __name__ == "__main__":
    load_dotenv()
    model = Model(getenv("GEMINI_API_KEY"))
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
    app = QApplication(argv)
    s = StreamViz(model, embedding_model)
    s.show()
    exit(app.exec())
