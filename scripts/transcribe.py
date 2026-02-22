import json
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AUDIO_DIR = Path("audio/raw")
OUT_DIR = Path("transcripts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()

def transcribe(audio_path: Path):
    with audio_path.open("rb") as f:
        result = client.audio.transcriptions.create(
            file=f,
            model="whisper-1",
            response_format="verbose_json"
        )

    segments = [
        {
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        }
        for seg in result.segments  # Access as object attribute, not dictionary key
    ]

    out_file = OUT_DIR / f"{audio_path.stem}.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python transcribe.py <audio_file.wav>")
        sys.exit(1)

    audio_path = Path(sys.argv[1])
    transcribe(audio_path)