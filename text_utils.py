import os
import re
import tempfile
import shutil
from dotenv import load_dotenv
from groq import Groq
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)
import yt_dlp
from PyPDF2 import PdfReader
from llm_utils import generate_notes_safe, generate_mcqs_safe, generate_flashcards_safe

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# SAFETY LIMITS
# =========================
MAX_PDF_SIZE_MB = 18          # block very large PDFs
MAX_TEXT_LENGTH = 20_000      # safe text limit for Groq


# -----------------------------
# PDF
# -----------------------------
def extract_text_from_pdf(pdf_file):
    pdf_file.seek(0)
    size_mb = len(pdf_file.read()) / (1024 * 1024)
    pdf_file.seek(0)

    if size_mb > MAX_PDF_SIZE_MB:
        raise ValueError("PDF_TOO_LARGE")

    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text() or ""
        text += extracted

        if len(text) > MAX_TEXT_LENGTH:
            raise ValueError("PDF_TOO_LARGE")

    return text




# -----------------------------
# YOUTUBE ID EXTRACTOR (ROBUST)
# -----------------------------
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else url


# -----------------------------
# GROQ WHISPER (SHARED)
# -----------------------------
def groq_whisper_from_file(path):
    try:
        if os.path.getsize(path) > 25 * 1024 * 1024:
            print("Audio too large for Groq Whisper")
            return ""

        with open(path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3"
            )

        return result.text

    except Exception as e:
        print("❌ Groq Whisper error:", e)
        return ""


# -----------------------------
# AUDIO FILE UPLOAD
# -----------------------------
def groq_whisper_transcribe_audio(audio_file):
    temp_path = None
    try:
        audio_file.seek(0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_file.read())
            temp_path = tmp.name

        return groq_whisper_from_file(temp_path)

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# -----------------------------
# YOUTUBE AUDIO DOWNLOAD
# -----------------------------
def download_youtube_audio(url):
    temp_dir = tempfile.mkdtemp()
    out_path = os.path.join(temp_dir, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": out_path,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir(temp_dir):
        if file.endswith((".mp3", ".m4a", ".webm")):
            return os.path.join(temp_dir, file), temp_dir

    return None, temp_dir


# -----------------------------
# YOUTUBE TEXT EXTRACTION
# -----------------------------
def extract_text_from_youtube(video_url):
    video_id = extract_video_id(video_url)

    # 1️⃣ Try captions first
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])

    except (TranscriptsDisabled, NoTranscriptFound, Exception):
        print("⚠️ Captions unavailable, using Whisper")

    # 2️⃣ Whisper fallback
    audio_path, temp_dir = download_youtube_audio(video_url)
    try:
        if audio_path:
            return groq_whisper_from_file(audio_path)
        return ""
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

