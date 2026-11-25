import logging
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.core.config import settings

logger = logging.getLogger("app.services.multimodal.sentiment")

# High-precision sentiment lexicon for candidate speech & interview transcripts
POSITIVE_WORDS = {
    "excited", "passionate", "proud", "successfully", "optimized", "improved",
    "scaled", "collaborated", "innovated", "achieved", "solved", "dedicated",
    "delighted", "love", "enjoy", "effective", "efficient", "thrive", "excellent",
    "proactive", "valuable", "strong", "positive", "rewarding", "enthusiastic",
    "advanced", "streamlined", "impact", "leadership", "resilient", "reliable",
    "great", "forward", "best", "confident", "clarity", "honored", "pleasure"
}

NEGATIVE_WORDS = {
    "struggled", "failed", "conflict", "frustrated", "delay", "poor", "broken",
    "difficult", "stressful", "problematic", "hate", "disappointed", "weak",
    "blame", "chaotic", "exhausted", "regret", "unhappy", "unable", "overwhelmed",
    "fault", "defect", "crisis", "disaster", "terrible", "worst", "ineffective"
}

INTENSIFIERS = {
    "very": 1.5,
    "extremely": 2.0,
    "deeply": 1.8,
    "highly": 1.7,
    "truly": 1.5,
    "really": 1.4,
    "especially": 1.5,
    "significantly": 1.6,
}

NEGATIONS = {"not", "never", "no", "hardly", "barely", "scarcely", "without", "rarely"}


class SentimentAnalysisResult(BaseModel):
    label: str = Field(..., description="POSITIVE, NEUTRAL, or NEGATIVE")
    polarity_score: float = Field(..., ge=0.0, le=1.0, description="Normalized score 0.0 (negative) to 1.0 (positive)")
    positive_prob: float = Field(..., ge=0.0, le=1.0)
    neutral_prob: float = Field(..., ge=0.0, le=1.0)
    negative_prob: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(default=90.0, ge=0.0, le=100.0)
    model_source: str = Field(
        default="lexicon_deterministic_fallback",
        description="transformer_pipeline or lexicon_deterministic_fallback",
    )
    key_sentiment_phrases: List[str] = Field(default_factory=list)


class MultimodalSentimentService:
    """
    Analyzes sentiment, polarity, and emotional confidence from candidate video transcripts
    using BERT transformers or an offline deterministic lexicon fallback.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.SENTIMENT_MODEL_NAME
        self.pipeline = None
        self._load_pipeline()

    def _load_pipeline(self):
        """Attempts loading Hugging Face transformers pipeline."""
        try:
            from transformers import pipeline

            # bert-base-multilingual-uncased-sentiment or distilbert-base-uncased-finetuned-sst-2-english
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=-1,  # CPU
            )
            logger.info(f"Loaded sentiment transformer pipeline: {self.model_name}")
        except Exception as e:
            logger.info(
                f"Transformer pipeline not available offline ({e}). Using deterministic rule-based sentiment engine."
            )
            self.pipeline = None

    def analyze(self, transcript_text: str) -> SentimentAnalysisResult:
        """
        Executes sentiment analysis returning polarity score and category label.
        """
        if not transcript_text or not transcript_text.strip():
            return SentimentAnalysisResult(
                label="NEUTRAL",
                polarity_score=0.5,
                positive_prob=0.33,
                neutral_prob=0.34,
                negative_prob=0.33,
                confidence=70.0,
                model_source="lexicon_deterministic_fallback",
                key_sentiment_phrases=[],
            )

        if self.pipeline is not None:
            try:
                # Truncate text to 512 tokens max for standard BERT
                truncated = transcript_text[:1000]
                res = self.pipeline(truncated)[0]
                raw_label = str(res.get("label", "")).upper()
                score = float(res.get("score", 0.90))

                # Handle star rating models (e.g. 1-5 stars)
                if "STAR" in raw_label:
                    stars = int(re.search(r"\d+", raw_label).group(0))
                    polarity = (stars - 1) / 4.0  # 0.0 to 1.0
                    label = "POSITIVE" if stars >= 4 else "NEGATIVE" if stars <= 2 else "NEUTRAL"
                elif "POS" in raw_label:
                    polarity = 0.5 + (score * 0.45)
                    label = "POSITIVE"
                elif "NEG" in raw_label:
                    polarity = 0.5 - (score * 0.45)
                    label = "NEGATIVE"
                else:
                    polarity = 0.5
                    label = "NEUTRAL"

                pos_p = polarity
                neg_p = 1.0 - polarity
                neu_p = max(0.0, 1.0 - abs(polarity - 0.5) * 2)

                return SentimentAnalysisResult(
                    label=label,
                    polarity_score=round(polarity, 3),
                    positive_prob=round(pos_p, 3),
                    neutral_prob=round(neu_p, 3),
                    negative_prob=round(neg_p, 3),
                    confidence=round(score * 100.0, 1),
                    model_source="transformer_pipeline",
                    key_sentiment_phrases=self._extract_key_phrases(transcript_text),
                )
            except Exception as pipe_err:
                logger.warning(f"Transformer inference error ({pipe_err}), using fallback.")

        # Fallback to deterministic lexicon analysis
        return self._deterministic_lexicon_analysis(transcript_text)

    def _deterministic_lexicon_analysis(self, text: str) -> SentimentAnalysisResult:
        """
        High-precision lexicon analysis factoring in intensifiers and negations.
        """
        words = re.findall(r"\b[A-Za-z'-]+\b", text.lower())
        if not words:
            return SentimentAnalysisResult(
                label="NEUTRAL",
                polarity_score=0.5,
                positive_prob=0.33,
                neutral_prob=0.34,
                negative_prob=0.33,
                confidence=75.0,
                model_source="lexicon_deterministic_fallback",
            )

        pos_score = 0.0
        neg_score = 0.0
        key_phrases = []

        for i, word in enumerate(words):
            # Check negation window of 2 words preceding
            is_negated = any(words[j] in NEGATIONS for j in range(max(0, i - 2), i))
            # Check intensifier immediately preceding
            multiplier = 1.0
            if i > 0 and words[i - 1] in INTENSIFIERS:
                multiplier = INTENSIFIERS[words[i - 1]]

            if word in POSITIVE_WORDS:
                if is_negated:
                    neg_score += 1.0 * multiplier
                    key_phrases.append(f"not {word}")
                else:
                    pos_score += 1.0 * multiplier
                    key_phrases.append(f"{words[i-1]} {word}" if multiplier > 1.0 else word)

            elif word in NEGATIVE_WORDS:
                if is_negated:
                    pos_score += 0.8 * multiplier
                    key_phrases.append(f"not {word}")
                else:
                    neg_score += 1.2 * multiplier
                    key_phrases.append(f"{words[i-1]} {word}" if multiplier > 1.0 else word)

        total_sentiment = pos_score + neg_score
        if total_sentiment == 0:
            polarity = 0.52  # Slightly optimistic baseline for professional candidate interviews
            label = "NEUTRAL"
            pos_p, neu_p, neg_p = 0.35, 0.55, 0.10
        else:
            raw_diff = (pos_score - neg_score) / (total_sentiment + 2.0)
            polarity = round(0.5 + (raw_diff * 0.45), 3)
            polarity = max(0.05, min(0.98, polarity))

            if polarity >= 0.58:
                label = "POSITIVE"
                pos_p = polarity
                neg_p = max(0.02, round(1.0 - polarity, 3))
                neu_p = max(0.05, round(1.0 - (pos_p + neg_p), 3))
            elif polarity <= 0.42:
                label = "NEGATIVE"
                neg_p = round(1.0 - polarity, 3)
                pos_p = max(0.02, polarity)
                neu_p = max(0.05, round(1.0 - (pos_p + neg_p), 3))
            else:
                label = "NEUTRAL"
                neu_p = 0.60
                pos_p = round((1.0 - neu_p) * 0.6, 3)
                neg_p = round((1.0 - neu_p) * 0.4, 3)

        return SentimentAnalysisResult(
            label=label,
            polarity_score=polarity,
            positive_prob=pos_p,
            neutral_prob=neu_p,
            negative_prob=neg_p,
            confidence=88.5,
            model_source="lexicon_deterministic_fallback",
            key_sentiment_phrases=list(set(key_phrases))[:6],
        )

    def _extract_key_phrases(self, text: str) -> List[str]:
        words = text.lower().split()
        return [w for w in words if w in POSITIVE_WORDS or w in NEGATIVE_WORDS][:5]


# Global singleton sentiment analyzer instance
sentiment_analyzer = MultimodalSentimentService()
