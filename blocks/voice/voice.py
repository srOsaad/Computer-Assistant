import os
import pyaudio
import webrtcvad
import collections
import wave
from faster_whisper import WhisperModel
from PySide6.QtCore import QThread, Signal
from blocks.auxiliary.auxiliary import say


class VoiceThread(QThread):
    recognized = Signal(str)
    listening = Signal(bool)
    transcribing = Signal(bool)
    stopTimer = Signal()

    def __init__(self, format=pyaudio.paInt16, channels=1, rate=16000, frame_duration=30,
                 vad_mode=2, pre_roll_frames=10, hangover_frames=15, whisper_model="small.en"):
        super().__init__()
        # audio
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = rate
        self.FRAME_DURATION = frame_duration
        self.FRAME_SIZE = int(rate * frame_duration / 1000)

        # vad 
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(vad_mode)
        self.PRE_ROLL_FRAMES = pre_roll_frames
        self.HANGOVER_FRAMES = hangover_frames
        self.activation_word = 'Jimmy'
        self.currentAudioDevice = 0
        self.stream = None
        self.p = None

        # whisper
        print(f"Loading Whisper model: {whisper_model}...")
        self.whisper = WhisperModel(whisper_model, device="cuda", compute_type="int8")

        self.expected_words = f"""{self.activation_word}"""
        self.active = False
        self._running = False

    def reset_active(self):
        self.active = False

    def setCurrentInputDevice(self, device_index):
        self.currentAudioDevice = device_index

        if self.stream is not None:
            if self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()

            self.stream = self.p.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.FRAME_SIZE,
                                      input_device_index=self.currentAudioDevice)
            info = self.p.get_device_info_by_index(self.currentAudioDevice)
            print("✅ Stream started on:", info['name'])
        else:
            print(f"🎤 Device index set to {device_index}, will be used when stream starts.")

    def stop(self):
        self._running = False
        self.wait()

    def frame_generator(self):
        while self._running:
            data = self.stream.read(self.FRAME_SIZE, exception_on_overflow=False)
            yield data

    def save_wav(self, frames, filename=None):
        if filename is None:
            filename = "speech.wav"
        cache_dir = "cache"
        os.makedirs(cache_dir, exist_ok=True)
        filename = os.path.join(cache_dir, "speech.wav")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return filename

    def transcribe(self, filepath):
        print("🔎 Transcribing with Whisper...")
        segments, _ = self.whisper.transcribe(filepath, language="en")#, initial_prompt=self.expected_words)
        text = " ".join(segment.text for segment in segments).strip()
        print(f"📝 Transcript: {text}\n")
        return text

    def vad_collector(self):
        ring_buffer = collections.deque(maxlen=self.PRE_ROLL_FRAMES)
        triggered = False
        speech_frames = []
        unvoiced_counter = 0

        for frame in self.frame_generator():
            if not self._running:
                break

            is_speech = self.vad.is_speech(frame, self.RATE)

            if not triggered:
                ring_buffer.append(frame)
                num_voiced = sum(1 for f in ring_buffer if self.vad.is_speech(f, self.RATE))
                if num_voiced > self.PRE_ROLL_FRAMES // 2:
                    triggered = True
                    print(">>> Speech started")
                    if self.active:
                        self.listening.emit(True)
                    speech_frames.extend(ring_buffer)
                    ring_buffer.clear()
            else:
                speech_frames.append(frame)
                if not is_speech:
                    unvoiced_counter += 1
                else:
                    unvoiced_counter = 0
                if unvoiced_counter > self.HANGOVER_FRAMES:
                    triggered = False
                    print("<<< Speech ended")
                    if self.active:
                        self.listening.emit(False)
                    filepath = self.save_wav(speech_frames)
                    if self.active:
                        self.transcribing.emit(True)
                    text = self.transcribe(filepath).strip()
                    if self.active:
                        self.transcribing.emit(False)
                    if self.active and text.strip():
                        self.recognized.emit(text)
                    if self.activation_word.lower() in text.lower():
                        self.active = True
                        self.stopTimer.emit()
                        i = text.lower().find(self.activation_word.lower())
                        i += len(self.activation_word)
                        text = text[i:].strip()
                        if len(text) > 4:
                            self.recognized.emit(text)
                            say('On my way to assist you.')
                        else:
                            say('Yes?')

                    speech_frames = []
                    unvoiced_counter = 0

    def run(self):
        print("🎧 Listening... (call stop() to end)")
        self._running = True

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.FRAME_SIZE,
                                  input_device_index=self.currentAudioDevice)

        info = self.p.get_device_info_by_index(self.currentAudioDevice)
        print("✅ Stream started on:", info['name'])


        try:
            self.vad_collector()
        finally:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            print("🛑 Audio stream terminated.")
