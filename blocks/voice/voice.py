import os
import logging
import threading
from PySide6.QtCore import QThread, Signal
from functools import partial
from enum import Enum
from blocks.auxiliary.auxiliary import say
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)

class TurnState(Enum):
    UNDEFINED = 0
    STARTED = 1
    FINISHED = 2

class VoiceThread(QThread):
    recognized = Signal(str)
    listening = Signal(bool)
    transcribing = Signal(bool)
    stopTimer = Signal()

    def __init__(self):
        super().__init__()
        self.sample_rate = 16000
        self.api_key = os.environ["ASSEMBLYAI_API_KEY"]
        logging.basicConfig(level=logging.INFO)
        self.activation_word = 'Shams'
        self.active = False
        self._running = False
        self.current_state = TurnState.UNDEFINED
        self.client = None
        self._stream_thread = None

    def reset_active(self):
        self.active = False

    def on_begin(self, client: StreamingClient, event: BeginEvent, *args, **kwargs):
        print("Started voice system!")

    def on_turn(self, client: StreamingClient, event: TurnEvent, *args, **kwargs):
        if self.current_state == TurnState.UNDEFINED:
            if self.active:
                self.listening.emit(True)
            self.current_state = TurnState.STARTED
        elif self.current_state == TurnState.FINISHED:
            x = event.transcript
            print(f"Recognized: {x}")
            self.current_state = TurnState.UNDEFINED
            if self.active:
                self.listening.emit(False)
            if self.activation_word.lower() in x.lower():
                self.active = True
                self.stopTimer.emit()
                i = x.lower().find(self.activation_word.lower())
                i += len(self.activation_word)
                x = x[i:].strip()
                if len(x) < 5:
                    say('Ready to assist.')
                else:
                    say('On my way to assist you.')
            if self.active:
                self.recognized.emit(x)

        if event.end_of_turn and not event.turn_is_formatted:
            params = StreamingSessionParameters(format_turns=True)
            self.current_state = TurnState.FINISHED
            client.set_params(params)

    def on_terminated(self, client: StreamingClient, event: TerminationEvent, *args, **kwargs):
        print(f"Session terminated: {event.audio_duration_seconds} seconds processed")

    def on_error(self, client: StreamingClient, error: StreamingError, *args, **kwargs):
        print(f"Error occurred: {error}")

    def stop(self):
        self._running = False
        if self.client:
            try:
                self.client.disconnect(terminate=True)
            except Exception as e:
                print(f"Error stopping client: {e}")
        if self._stream_thread:
            self._stream_thread.join(timeout=1)
            self._stream_thread = None
        print("Voice thread stopped.")

    def _run_stream(self):
        try:
            self.client.stream(aai.extras.MicrophoneStream(sample_rate=self.sample_rate))
        except Exception as e:
            print(f"Stream error: {e}")

    def start_stream(self):
        self.client = StreamingClient(
            StreamingClientOptions(
                api_key=self.api_key,
                api_host="streaming.assemblyai.com",
            )
        )

        self.client.on(StreamingEvents.Begin, partial(self.on_begin))
        self.client.on(StreamingEvents.Turn, partial(self.on_turn))
        self.client.on(StreamingEvents.Termination, partial(self.on_terminated))
        self.client.on(StreamingEvents.Error, partial(self.on_error))

        self.client.connect(
            StreamingParameters(
                sample_rate=self.sample_rate,
                format_turns=True,
            )
        )

        self._stream_thread = threading.Thread(target=self._run_stream, daemon=True)
        self._stream_thread.start()

    def run(self):
        self._running = True
        print("🎧 Listening... (call stop() to end)")
        self.start_stream()
        while self._running and self._stream_thread and self._stream_thread.is_alive():
            self.msleep(100)
        print("Voice thread finished.")
