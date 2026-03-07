import os
import json
import re
from pathlib import Path
from typing import Dict, Any

from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

from deepgram import DeepgramClient

dg_client = DeepgramClient()

AUDIO_DIR = Path("audio/raw")
TRANSCRIPT_DIR = Path("transcripts")
DATASET_DIR = Path("dataset")

for d in [AUDIO_DIR, TRANSCRIPT_DIR, DATASET_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def get_video_id(url: str) -> str:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else "unknown"

def download_audio(youtube_url: str) -> Dict[str, Any]:
    video_id = get_video_id(youtube_url)
    audio_path = AUDIO_DIR / f"{video_id}.wav"

    if audio_path.exists():
        print(f"   (Using cached audio: {audio_path})")
        return {"status": "success", "video_id": video_id, "audio_path": str(audio_path)}

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(AUDIO_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "postprocessor_args": ["-ac", "1", "-ar", "16000"],
        "quiet": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        video_id = info['id']
        audio_path = AUDIO_DIR / f"{video_id}.wav"
    return {"status": "success", "video_id": video_id, "audio_path": str(audio_path)}

def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    path = Path(audio_path)
    out_file = TRANSCRIPT_DIR / f"{path.stem}.json"

    if out_file.exists():
        print(f"   (Using cached transcript: {out_file})")
        with open(out_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        return {"status": "success", "transcript_path": str(out_file), "segments": segments}

    print("   (Connecting to Deepgram Nova-3...)")
    try:
        with open(path, "rb") as file:
            buffer_data = file.read()

        response = dg_client.listen.v1.media.transcribe_file(
            request=buffer_data,
            model="nova-3",
            smart_format=True,
            utterances=True,
            language="ur" # Explicitly set language to Urdu
        )
        
        raw_words = response.results.channels[0].alternatives[0].words
        
        if hasattr(response.results.channels[0].alternatives[0], 'utterances') and response.results.channels[0].alternatives[0].utterances:
            raw_utterances = response.results.channels[0].alternatives[0].utterances
            segments = [
                {
                    "start": utt.start,
                    "end": utt.end,
                    "text": utt.transcript.strip()
                }
                for utt in raw_utterances
            ]
        else:
            segments = []
            chunk_size = 15
            for i in range(0, len(raw_words), chunk_size):
                chunk = raw_words[i : i + chunk_size]
                segments.append({
                    "start": chunk[0].start,
                    "end": chunk[-1].end,
                    "text": " ".join([w.word for w in chunk]).strip()
                })

        with out_file.open("w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
            
        return {"status": "success", "transcript_path": str(out_file), "segments": segments}
    
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise

def build_dataset(transcript_path: str, audio_path: str) -> Dict[str, Any]:
    with open(transcript_path, 'r') as f:
        segments = json.load(f)
    dataset_file = DATASET_DIR / f"{Path(audio_path).stem}_dataset.json"
    filtered_segments = [seg for seg in segments if 1 <= seg["end"] - seg["start"] <= 12]
    dataset = [{
        "id": f"{Path(audio_path).stem}_{i}",
        "audio_path": audio_path,
        "start": seg["start"],
        "end": seg["end"],
        "text": seg["text"],
        "duration": seg["end"] - seg["start"]
    } for i, seg in enumerate(filtered_segments)]
    
    with open(dataset_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    return {"status": "success", "dataset_path": str(dataset_file), "count": len(dataset)}