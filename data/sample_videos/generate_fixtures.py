"""
Generates synthetic placeholder media fixtures (minimal valid WAV/MP4 files or stubs)
and updates fixtures_manifest.json for offline testing of multimodal pipelines.
"""

import json
import os
import wave
import struct
from pathlib import Path

VIDEO_DIR = Path(__file__).resolve().parent
MANIFEST_FILE = VIDEO_DIR / "fixtures_manifest.json"


def create_synthetic_wav(filepath: Path, duration_sec: float = 2.0, sample_rate: int = 16000):
    """Generates a minimal valid mono PCM 16-bit WAV file."""
    num_samples = int(duration_sec * sample_rate)
    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        # Generate silence / subtle tone samples
        data = struct.pack(f"<{num_samples}h", *([0] * num_samples))
        wav_file.writeframes(data)


def create_placeholder_video(filepath: Path):
    """Creates a tagged stub file representing a fixture video for tests."""
    with open(filepath, "wb") as f:
        # Write minimal header identifying it as a test fixture placeholder
        header = b"MOCK_MP4_FIXTURE_HEADER_TEST_ONLY\x00\x00\x00\x1cftypisom\x00\x00\x02\x00"
        f.write(header)


def main():
    print(f"Generating sample video/audio test fixtures in {VIDEO_DIR}...")

    if not MANIFEST_FILE.exists():
        print(f"Error: {MANIFEST_FILE} not found.")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for item in manifest.get("fixtures", []):
        video_name = item.get("video_filename")
        audio_name = item.get("audio_extracted_path")

        if video_name:
            v_path = VIDEO_DIR / video_name
            if not v_path.exists():
                create_placeholder_video(v_path)
                print(f"  Created placeholder video: {video_name}")

        if audio_name:
            a_path = VIDEO_DIR / audio_name
            if not a_path.exists():
                create_synthetic_wav(a_path, duration_sec=3.0)
                print(f"  Created synthetic audio WAV: {audio_name}")

    print("Sample fixtures generation complete.")


if __name__ == "__main__":
    main()
