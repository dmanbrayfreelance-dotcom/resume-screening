import json
import logging
import os
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from backend.app.core.config import settings

logger = logging.getLogger("app.services.ingestion.video_transcriber")


class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    confidence: Optional[float] = None


class TranscriptionResult(BaseModel):
    transcript: str
    duration_seconds: float = Field(default=0.0, ge=0.0)
    word_count: int = Field(default=0, ge=0)
    words_per_minute: float = Field(default=0.0, ge=0.0)
    speaking_pace: str = Field(default="optimal", description="slow, optimal, fast")
    transcription_source: str = Field(
        default="mock_offline",
        description="whisper_live, faster_whisper, fixture_manifest, synthetic_fallback",
    )
    audio_wav_path: Optional[str] = None
    confidence_score: float = Field(default=90.0, ge=0.0, le=100.0)
    segments: List[TranscriptionSegment] = Field(default_factory=list)


class VideoTranscriberService:
    """
    Transcribes candidate video interviews (MP4, WEBM) by extracting audio to WAV,
    running Whisper / faster-whisper, and gracefully falling back to deterministic fixtures
    or synthetic offline mock analysis when models or ffmpeg are absent.
    """

    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = (
            manifest_path
            or Path(__file__).resolve().parents[4] / "data" / "sample_videos" / "fixtures_manifest.json"
        )
        self._fixtures_cache: Dict[str, Dict[str, Any]] = {}
        self._load_fixtures()

    def _load_fixtures(self):
        """Loads pre-computed interview fixtures if present."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("fixtures", []):
                        if "video_filename" in item:
                            self._fixtures_cache[item["video_filename"]] = item
                        if "candidate_id" in item:
                            self._fixtures_cache[item["candidate_id"]] = item
            except Exception as e:
                logger.warning(f"Could not load video fixtures manifest: {e}")

    def extract_audio_wav(
        self, video_path: Union[str, Path], output_wav_path: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """
        Extracts mono 16kHz WAV from MP4/WEBM using moviepy or ffmpeg CLI.
        Returns None if extraction is not possible or file is synthetic stub.
        """
        video_p = Path(video_path)
        if not video_p.exists():
            logger.warning(f"Video file not found: {video_p}")
            return None

        out_wav = Path(output_wav_path) if output_wav_path else video_p.with_suffix(".wav")

        # 1. Try moviepy
        try:
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(str(video_p))
            if clip.audio is not None:
                clip.audio.write_audiofile(
                    str(out_wav), fps=16000, nbytes=2, codec="pcm_s16le", logger=None
                )
                clip.close()
                return out_wav
        except Exception:
            pass

        # 2. Try system ffmpeg CLI
        if shutil.which("ffmpeg"):
            try:
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(video_p),
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    str(out_wav),
                ]
                subprocess.run(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                )
                if out_wav.exists() and out_wav.stat().st_size > 0:
                    return out_wav
            except Exception as ffmpeg_err:
                logger.warning(f"ffmpeg extraction failed: {ffmpeg_err}")

        # Check if a sibling WAV already exists
        sibling_wav = video_p.with_suffix(".wav")
        if sibling_wav.exists():
            return sibling_wav

        return None

    def transcribe(
        self,
        video_or_audio_path: Union[str, Path],
        candidate_id: Optional[str] = None,
        force_offline_fallback: bool = False,
    ) -> TranscriptionResult:
        """
        Transcribes media file using Whisper, or activates deterministic offline fixture fallback.
        """
        media_path = Path(video_or_audio_path)
        filename = media_path.name

        # Check deterministic fixture manifest first if offline fallback requested or filename matches
        fixture = self._fixtures_cache.get(filename) or (
            self._fixtures_cache.get(candidate_id) if candidate_id else None
        )

        if force_offline_fallback and fixture:
            return self._build_from_fixture(fixture, str(media_path))

        # Attempt extraction of WAV if input is video
        wav_path = None
        if media_path.suffix.lower() in [".mp4", ".webm", ".mov", ".mkv"]:
            wav_path = self.extract_audio_wav(media_path)
            target_audio = wav_path or media_path
        else:
            target_audio = media_path
            wav_path = media_path if media_path.suffix.lower() == ".wav" else None

        # Attempt faster-whisper or openai-whisper
        if not force_offline_fallback:
            result = self._try_whisper_transcription(target_audio, wav_path)
            if result is not None:
                return result

        # Fallback to fixture manifest if matched
        if fixture:
            return self._build_from_fixture(fixture, str(wav_path or media_path))

        # Final deterministic synthetic fallback
        return self._generate_synthetic_fallback(media_path, wav_path)

    def _try_whisper_transcription(
        self, audio_path: Path, wav_path: Optional[Path]
    ) -> Optional[TranscriptionResult]:
        """Tries faster_whisper first, then openai-whisper."""
        # 1. Try faster_whisper
        try:
            from faster_whisper import WhisperModel

            model_size = settings.WHISPER_MODEL_SIZE
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            segments_gen, info = model.transcribe(str(audio_path), beam_size=5)

            segments = []
            full_text = []
            for seg in segments_gen:
                full_text.append(seg.text)
                segments.append(
                    TranscriptionSegment(start=seg.start, end=seg.end, text=seg.text.strip())
                )

            transcript = " ".join(full_text).strip()
            duration = info.duration or 30.0
            return self._create_result(
                transcript=transcript,
                duration=duration,
                source="faster_whisper",
                audio_path=str(wav_path or audio_path),
                segments=segments,
            )
        except Exception:
            pass

        # 2. Try openai whisper
        try:
            import whisper

            model_size = settings.WHISPER_MODEL_SIZE
            model = whisper.load_model(model_size)
            res = model.transcribe(str(audio_path))
            transcript = res.get("text", "").strip()

            segments = [
                TranscriptionSegment(
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                    text=seg.get("text", "").strip(),
                )
                for seg in res.get("segments", [])
            ]

            duration = segments[-1].end if segments else 30.0
            return self._create_result(
                transcript=transcript,
                duration=duration,
                source="whisper_live",
                audio_path=str(wav_path or audio_path),
                segments=segments,
            )
        except Exception:
            pass

        return None

    def _build_from_fixture(self, fixture: Dict[str, Any], audio_path: str) -> TranscriptionResult:
        """Constructs TranscriptionResult from pre-computed fixture manifest."""
        transcript = fixture.get("transcript", "")
        duration = float(fixture.get("video_duration_seconds", 30.0))
        wpm = float(fixture.get("words_per_minute", 135.0))
        pace = fixture.get("speaking_pace", "optimal")
        confidence = float(
            fixture.get("multimodal_scores", {}).get("confidence_score", 90.0)
        )

        words = transcript.split()
        return TranscriptionResult(
            transcript=transcript,
            duration_seconds=duration,
            word_count=len(words),
            words_per_minute=wpm,
            speaking_pace=pace,
            transcription_source="fixture_manifest",
            audio_wav_path=audio_path,
            confidence_score=confidence,
            segments=[
                TranscriptionSegment(start=0.0, end=duration, text=transcript, confidence=confidence / 100.0)
            ],
        )

    def _generate_synthetic_fallback(
        self, media_path: Path, wav_path: Optional[Path]
    ) -> TranscriptionResult:
        """Deterministic offline mock analysis when neither models nor fixtures are present."""
        duration = 30.0
        # Check actual WAV duration if valid wave file
        if wav_path and wav_path.exists():
            try:
                with wave.open(str(wav_path), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    if rate > 0 and frames > 0:
                        duration = max(round(frames / float(rate), 2), 1.0)
            except Exception:
                pass

        transcript = (
            f"Candidate introduction audio response for {media_path.stem}. "
            "Overview of experience in software development, architecture, and technology capabilities."
        )
        return self._create_result(
            transcript=transcript,
            duration=duration,
            source="synthetic_fallback",
            audio_path=str(wav_path or media_path),
            confidence_score=85.0,
        )

    def _create_result(
        self,
        transcript: str,
        duration: float,
        source: str,
        audio_path: Optional[str] = None,
        confidence_score: float = 90.0,
        segments: Optional[List[TranscriptionSegment]] = None,
    ) -> TranscriptionResult:
        """Calculates speaking rate and categorizes pace."""
        words = transcript.split()
        word_count = len(words)
        duration_mins = max(duration / 60.0, 0.05)
        wpm = round(word_count / duration_mins, 1)

        # Speaking pace categorization:
        # < 115 WPM: slow
        # 115 - 165 WPM: optimal
        # > 165 WPM: fast
        if wpm < 115:
            pace = "slow"
        elif wpm > 165:
            pace = "fast"
        else:
            pace = "optimal"

        return TranscriptionResult(
            transcript=transcript,
            duration_seconds=round(duration, 2),
            word_count=word_count,
            words_per_minute=wpm,
            speaking_pace=pace,
            transcription_source=source,
            audio_wav_path=audio_path,
            confidence_score=confidence_score,
            segments=segments or [],
        )


# Global singleton video transcriber instance
video_transcriber = VideoTranscriberService()
