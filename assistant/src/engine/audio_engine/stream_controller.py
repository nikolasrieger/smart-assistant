from numpy import (
    zeros,
    int32,
    frombuffer,
    median,
    array,
    concatenate,
)
from pyaudio import paInt16, PyAudio
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QThread, QEventLoop, QTimer, pyqtSignal
from speech_recognition import AudioData, Recognizer, UnknownValueError


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
        self.recognizer = Recognizer()

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

        self.process_audio_for_text(vals)

        while len(self.buffer) >= self.samples_per_interval:
            interval_data = self.buffer[: self.samples_per_interval]
            median_value = median(interval_data)
            self.median_data.append(median_value)
            self.buffer = self.buffer[self.samples_per_interval :]

        if len(self.median_data) * self.samples_per_interval > len(self.data):
            self.median_data = self.median_data[
                -len(self.data) // self.samples_per_interval :
            ]

    def process_audio_for_text(self, audio_data):
        audio_bytes = audio_data.tobytes()

        audio_source = AudioData(audio_bytes, self.RATE, 2) 

        try:
            text = self.recognizer.recognize_google(audio_source)
            print("Recognized Text: ", text)
        except UnknownValueError:
            print("Google Speech Recognition could not understand audio")


    def breakdown_stream(self):
        self.micthread.terminate()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        loop = QEventLoop()
        QTimer.singleShot(400, loop.quit)
        loop.exec()
