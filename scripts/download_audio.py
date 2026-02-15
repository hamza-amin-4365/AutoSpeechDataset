import sys
from pathlib import Path
from yt_dlp import YoutubeDL

AUDIO_DIR = Path("audio/raw")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def download_audio(youtube_url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(AUDIO_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "postprocessor_args": [
            "-ac", "1",        # mono
            "-ar", "16000",    # 16kHz
        ],
        "quiet": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_audio.py <youtube_url>")
        sys.exit(1)

    download_audio(sys.argv[1])
