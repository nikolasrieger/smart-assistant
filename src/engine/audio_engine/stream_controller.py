from __future__ import annotations
from numpy import zeros, int32, frombuffer, median, array, concatenate
from pyaudio import paInt16, PyAudio
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QThread, pyqtSignal
from speech_recognition import Recognizer, Microphone, UnknownValueError, RequestError
from colorama import Fore
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel
from helper import Assistant, INFO_MESSAGES


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


class TaskThread(QThread):
    finished = pyqtSignal()

    def __init__(self, assistant: Assistant, text: str):
        super(TaskThread, self).__init__()
        self.assistant = assistant
        self.text = text

    def run(self):
        self.assistant.do_task(self.text)
        self.finished.emit()


class SpeechRecognitionThread(QThread):
    def __init__(
        self, sc: StreamController, model: Model, embedding_model: EmbeddingModel
    ):
        super(SpeechRecognitionThread, self).__init__()
        self.sc = sc
        self.recognizer = Recognizer()
        self.microphone = Microphone()
        self.assistant = Assistant(model, embedding_model)
        self.running = True
        self.started_task = False

    def run(self):
        while self.running:
            text = self.sc.process_audio_for_text()
            if text != "":
                if self.started_task:
                    self.assistant.input_handler.add_input(text)
                else:
                    self.task_thread = TaskThread(self.assistant, text)
                    self.task_thread.start()
                    self.started_task = True

    def stop(self):
        self.running = False


class StreamController(QWidget):
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
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
        self.model = model
        self.embedding_model = embedding_model

        self.micthread = MicThread(self)
        self.speech_recognition_thread = SpeechRecognitionThread(
            self, self.model, self.embedding_model
        )

    def setup_stream(self):
        self.audio = PyAudio()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
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
            if INFO_MESSAGES:
                print(Fore.YELLOW + "[INFO-SPEECH]: " + Fore.RESET, transcription)
            return transcription
        except (UnknownValueError, RequestError):
            return ""

    def breakdown_stream(self):
        self.micthread.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.speech_recognition_thread.stop()

    def restore_stream(self):
        self.setup_stream()
