import json
from pathlib import Path

from vosk import Model, KaldiRecognizer, SetLogLevel

from async_wrapper import async_wrap


class Recognizer:
    model_path: Path
    model: Model | None

    def __init__(self, model_name: str):
        self.model_path = Path("models") / model_name
        print("Initializing model")
        self.model = Model(model_path=str(self.model_path))
        print("Model initialized")

    @async_wrap
    def recognize(self, audio_data: bytes) -> str:
        rec = KaldiRecognizer(self.model, 16000)
        rec.AcceptWaveform(audio_data)
        return json.loads(rec.FinalResult())["text"]
