from PySide6.QtCore import QThread, Signal
import speech_recognition as sr

class VoiceThread(QThread):
    recognized = Signal(str)
    listening_started = Signal()
    listening_stopped = Signal()

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1
            while self._running:
                try:
                    self.listening_started.emit()
                    print("[Listening...]")

                    audio = r.listen(source)

                    self.listening_stopped.emit()
                    print("[Stopped listening, processing...]")

                    query = r.recognize_google(audio, language='en-US')
                    print(f">> {query}")
                    self.recognized.emit(query)
                except Exception as e:
                    print(f"Noise/Error: {e}")

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
