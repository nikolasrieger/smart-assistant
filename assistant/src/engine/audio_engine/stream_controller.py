from numpy import zeros, int32, frombuffer, median, array, concatenate
from pyaudio import paInt16, PyAudio
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QThread, pyqtSignal
from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError
from colorama import Fore


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


class SpeechRecognitionThread(QThread):
    def __init__(self, sc):
        super(SpeechRecognitionThread, self).__init__()
        self.sc = sc
        self.recognizer = Recognizer()
        self.microphone = Microphone()
        self.running = True

    def run(self):
        while self.running:
            self.sc.process_audio_for_text()

    def stop(self):
        self.running = False


class StreamController(QWidget):
    def __init__(self, info):
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
        self.speech_recognition_thread = SpeechRecognitionThread(self)
        self.info = info

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
        self.speech_recognition_thread.start()

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

    def process_audio_for_text(self):
        try:
            with self.speech_recognition_thread.microphone as source:
                self.speech_recognition_thread.recognizer.adjust_for_ambient_noise(
                    source
                )
                audio = self.speech_recognition_thread.recognizer.listen(source)

            transcription = self.speech_recognition_thread.recognizer.recognize_google(
                audio
            )
            if self.info: print(Fore.YELLOW + "[INFO-SPEECH]: " + Fore.RESET, transcription)
            return transcription
        except (UnknownValueError, RequestError):
            return ""

    def breakdown_stream(self):
        self.micthread.terminate()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.speech_recognition_thread.stop()

    def restore_stream(self):
        self.setup_stream()
