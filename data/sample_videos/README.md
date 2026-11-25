# Sample Videos and Multimodal Fixtures

This directory contains test fixture metadata and lightweight media placeholders to enable instantaneous offline testing of the multimodal screening pipeline.

## Contents
- `fixtures_manifest.json`: Pre-computed transcription, sentiment, speaking pace (WPM), and presentation scores for test candidates.
- `generate_fixtures.py`: Utility script that creates synthetic WAV audio and MP4 fixture placeholders so file-handling services can run without large binary downloads.

## Usage
Run fixture generation:
```bash
python generate_fixtures.py
```
This produces minimal audio/video fixtures matching the candidate manifest.
