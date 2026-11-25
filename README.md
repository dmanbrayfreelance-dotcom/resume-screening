# Multimodal Resume Intelligence & Screening Studio

An end-to-end recruitment intelligence platform combining textual resume parsing, OpenAI Whisper speech transcription, video sentiment and pacing analysis, cross-modal claim verification, section-weighted semantic matching, and algorithmic fairness auditing.

---

## Architecture Overview

```
multimodal-resume-intelligence/
├── README.md
├── .env.example
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── candidate.py
│   │   │   └── job_profile.py
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   │   ├── resume_parser.py
│   │   │   │   └── video_transcriber.py
│   │   │   ├── nlp/
│   │   │   │   ├── preprocessor.py
│   │   │   │   ├── skill_extractor.py
│   │   │   │   └── matcher.py
│   │   │   ├── multimodal/
│   │   │   │   ├── sentiment_analyzer.py
│   │   │   │   ├── prosody_vision.py
│   │   │   │   └── claim_verifier.py
│   │   │   ├── ranking/
│   │   │   │   ├── hybrid_scorer.py
│   │   │   │   └── fairness_audit.py
│   │   │   └── reporting/
│   │   │       └── exporter.py
│   │   └── api/routes/
│   │       ├── health.py
│   │       ├── jobs.py
│   │       ├── candidates.py
│   │       └── analytics.py
│   └── tests/
│       ├── test_config_and_db.py
│       ├── test_ingestion_and_nlp.py
│       ├── test_matching_and_multimodal.py
│       ├── test_ranking_and_reporting.py
│       ├── test_matcher.py
│       ├── test_claim_verifier.py
│       └── test_api.py
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── api/
│       │   └── client.ts
│       ├── components/
│       │   ├── Navbar.tsx
│       │   ├── LeaderboardTable.tsx
│       │   ├── UploadPanel.tsx
│       │   ├── CandidateDrawer.tsx
│       │   ├── SkillGapChart.tsx
│       │   └── FairnessPanel.tsx
│       └── pages/
│           ├── DashboardPage.tsx
│           └── JobRubricPage.tsx
└── data/
    ├── sample_resumes/
    ├── sample_videos/
    └── sample_jds/
```

---

## Core Capabilities

### 1. Ingestion & NLP Preprocessing
- **Multi-Format Resume Parsing**: Handles PDF (`pypdf` / `fitz`), DOCX (`python-docx`), and plaintext resumes. Segments text into structured sections (`summary`, `skills`, `experience_projects`, `education`).
- **PII Redaction Engine**: Automatically extracts and strips personally identifiable attributes (`name`, `email`, `phone`, `location`) for demographic-neutral matching.
- **ASR & Video Transcription**: Transcribes interview recordings (`MP4`, `WEBM`) via Whisper / `faster-whisper`, with deterministic fixture and synthetic fallback modes for offline environments.
- **Protected Tech Taxonomy**: Recognizes specialized terms without token distortion (`C++`, `.NET`, `Node.js`, `Next.js`, `CI/CD`, `AI/ML`), extracting skills across 6 technical categories.

### 2. Semantic Matching & Multimodal Telemetry
- **Section-Weighted Dense Embeddings**: 384-dimensional dense embeddings (`all-MiniLM-L6-v2` with deterministic hash fallback) computing cosine similarities across skills, experience, and education.
- **Skill-Gap Explainability**: Identifies matched skills, missing required skills, missing preferred skills, coverage percentage, and actionable learning recommendations.
- **BERT Sentiment Analysis**: Powered by `nlptown/bert-base-multilingual-uncased-sentiment` (normalized to a 0.0–1.0 polarity scale) with an offline high-precision lexicon fallback.
- **Acoustic & Vision Metrics**: Evaluates speaking pace (WPM), filler-word frequency, vocal energy variation, and visual face-tracking engagement with explicit telemetry source labels (`librosa_acoustic_measured`, `wave_pcm_measured`, `opencv_frame_measured`, or heuristic fallback).
- **Cross-Modal Claim Verification**: Compares spoken claims in video transcripts against written resumes to verify credibility, detect tenure inflation, and flag unbacked executive seniority claims.

### 3. Ranking, Governance & Reporting
- **Transparent Hybrid Scoring**: Synthesizes 5 component scores into an explainable score card with recruiter executive summary, key strengths, and probing interview questions.
- **Algorithmic Fairness Guardrails**: Strict compliance with AI recruitment regulations: all scores are **advisory-only** (auto-rejection strictly prohibited), PII is scrubbed in review views, and batch statistical drift is audited across threshold sensitivities (60%, 70%, 75%, 80%, 85%).
- **Multi-Format Exports**: One-click download of candidate leaderboards, evaluation breakdowns, and fairness audit summaries as JSON and CSV payloads.

### 4. Interactive Screening Studio Frontend
- **React 18 + Vite + Tailwind CSS + Recharts**: Modern dark-mode recruiting studio.
- **Screening Leaderboard**: Multi-column sorting, filtering by recommendation badge (`Strong Hire`, `Hire`, `Further Review`, `Hold / Revisit`), and search.
- **Multi-Modal Candidate Drawer**: 5-tab deep drilldown (Scorecard, Skill Gap Radar & Bar, Speech & Video Telemetry, Claim Verifier, and Anonymized Fairness View).
- **Rubric & Weight Editor**: Interactive sliders with live Recharts pie visualization and one-click candidate re-ranking.
- **Ingest Dropzone**: Drag-and-drop resume documents with optional interview videos and live multi-stage progress tracking.

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (tested on Node.js 24)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key configuration parameters:
- `MONGODB_URI`: MongoDB Atlas connection URI (`mongodb+srv://...`)
- `ENABLE_LOCAL_FALLBACK_STORE`: Set to `true` (default) for zero-dependency local JSON storage if Atlas is offline.
- `WHISPER_MODEL_SIZE`: Whisper model scale (`tiny`, `base`, `small`, `medium`).
- `EMBEDDING_MODEL_NAME`: Dense embedding model (`all-MiniLM-L6-v2`).
- `SENTIMENT_MODEL_NAME`: HuggingFace transformer model for sentiment classification.

### 4. Running Backend
```bash
# From repository root
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### 5. Running Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

To verify production bundle build:
```bash
cd frontend
npm run build
```

### 6. Running Test Suite
Execute the full pytest suite (27 unit & integration tests):
```bash
python -m pytest backend/tests/ -v
```

---

## Sample Data & Benchmark JDs
- **25 Benchmark Job Descriptions**: Seeded automatically at startup across AI/ML, Software, Data Science, Cloud/DevOps, Cybersecurity, and Product/QA via `data/sample_jds/seed_25_jds.py` / `benchmark_25_jds.json`.
- **Sample Resumes**: `data/sample_resumes/sarah_chen_ai_engineer.txt`, `data/sample_resumes/alex_rivera_fullstack.txt`
- **Video Manifest**: `data/sample_videos/fixtures_manifest.json`
- **Fixture Generator**:
  ```bash
  python data/sample_videos/generate_fixtures.py
  ```
