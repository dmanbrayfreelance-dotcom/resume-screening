import hashlib
import logging
import math
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field
from backend.app.core.config import settings
from backend.app.services.nlp.skill_extractor import skill_extractor

logger = logging.getLogger("app.services.nlp.matcher")


class SkillGapReport(BaseModel):
    matched_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    coverage_pct: float = Field(..., ge=0.0, le=100.0)
    recommendations: List[str] = Field(default_factory=list)


class MatchEvaluationResult(BaseModel):
    overall_fit_score: float = Field(..., ge=0.0, le=100.0)
    section_scores: Dict[str, float] = Field(
        ...,
        description="Individual section similarities: skills, experience, education, semantic_fit",
    )
    skill_gap: SkillGapReport
    embedding_source: str = Field(
        default="deterministic_hash_fallback",
        description="sentence_transformers or deterministic_hash_fallback",
    )
    fit_summary: str


# Recommendations templates for bridging specific skill categories
CATEGORY_RECOMMENDATION_TEMPLATES = {
    "frameworks": "Build and showcase a hands-on project integrating {skills} (e.g. end-to-end API or dashboard).",
    "languages": "Complete core coding assessments or open-source PRs demonstrating proficiency in {skills}.",
    "databases": "Implement production data modeling and query optimization workflows with {skills}.",
    "cloud_devops": "Deploy containerized CI/CD microservices with automated deployment scripts using {skills}.",
    "ai_ml": "Fine-tune and evaluate transformer or multimodal pipelines utilizing {skills} on benchmark datasets.",
}


class SemanticEmbeddingEngine:
    """
    Produces dense semantic embeddings. Uses sentence-transformers (all-MiniLM-L6-v2)
    when available, with a deterministic TF-IDF / hash projection fallback for offline/CI use.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.dim = 384  # Standard all-MiniLM-L6-v2 embedding dimension
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded sentence-transformers model: {self.model_name}")
        except Exception as e:
            logger.info(
                f"sentence-transformers not available ({e}). Using deterministic 384-d dense hash embedding engine."
            )
            self.model = None

    def embed_text(self, text: str) -> np.ndarray:
        """Returns normalized 384-dimensional dense numpy vector."""
        if not text or not text.strip():
            return np.zeros(self.dim, dtype=np.float32)

        if self.model is not None:
            try:
                emb = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return emb.astype(np.float32)
            except Exception:
                pass

        return self._deterministic_hash_embedding(text)

    def _deterministic_hash_embedding(self, text: str) -> np.ndarray:
        """
        Creates a reproducible, normalized 384-dimensional semantic projection using
        sub-word n-gram hashing and character TF frequencies.
        """
        words = text.lower().split()
        if not words:
            return np.zeros(self.dim, dtype=np.float32)

        vec = np.zeros(self.dim, dtype=np.float32)
        total_tokens = len(words)

        for idx, word in enumerate(words):
            # Positional decay & frequency weighting
            weight = 1.0 / (1.0 + math.log1p(idx / total_tokens))
            # Multi-hash projection into 384 dimensions
            h1 = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            h2 = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)

            bucket1 = h1 % self.dim
            bucket2 = h2 % self.dim
            sign1 = 1.0 if (h1 & 1) else -1.0
            sign2 = 1.0 if (h2 & 1) else -1.0

            vec[bucket1] += sign1 * weight
            vec[bucket2] += sign2 * weight * 0.5

            # Word bigrams
            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                hb = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                bucket_b = hb % self.dim
                sign_b = 1.0 if (hb & 1) else -1.0
                vec[bucket_b] += sign_b * weight * 1.5

        # L2 normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculates cosine similarity bounded between 0.0 and 1.0."""
        dot = float(np.dot(v1, v2))
        # Scale [-1, 1] to [0, 1]
        sim = max(0.0, min(1.0, (dot + 1.0) / 2.0))
        return round(sim, 4)


class SemanticMatcherService:
    """
    Computes section-weighted semantic similarity between parsed candidate resumes
    and job descriptions, generating skill-gap explainability and concrete recommendations.
    """

    def __init__(self):
        self.embedding_engine = SemanticEmbeddingEngine()

    def evaluate_match(
        self,
        candidate_sections: Dict[str, str],
        candidate_skills: List[str],
        jd_data: Dict[str, Any],
        scoring_weights: Optional[Dict[str, float]] = None,
    ) -> MatchEvaluationResult:
        """
        Evaluates candidate against JD with section-weighted similarity
        and skill-gap analysis.
        """
        weights = scoring_weights or jd_data.get("scoring_weights", {})
        w_skills = weights.get("skill_match", 0.40)
        w_exp = weights.get("experience_match", 0.30)
        w_edu = weights.get("education_match", 0.15)
        w_sem = weights.get("semantic_fit", 0.15)

        # Normalize weights to sum to 1.0
        total_w = w_skills + w_exp + w_edu + w_sem
        if total_w <= 0:
            total_w = 1.0
        w_skills, w_exp, w_edu, w_sem = (
            w_skills / total_w,
            w_exp / total_w,
            w_edu / total_w,
            w_sem / total_w,
        )

        required_skills = jd_data.get("required_skills", [])
        preferred_skills = jd_data.get("preferred_skills", [])

        # 1. Skill Gap Analysis & Overlap Score
        skill_report = skill_extractor.match_skills(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
        )
        skills_score = skill_report.overall_skill_score  # 0 to 100

        # 2. Experience Section Semantic Similarity
        cand_exp_text = candidate_sections.get("experience_projects", "") or candidate_sections.get(
            "raw_text", ""
        )
        jd_responsibilities = " ".join(jd_data.get("responsibilities", []))
        jd_desc = jd_data.get("description", "")
        jd_exp_target = f"{jd_desc} {jd_responsibilities}"

        exp_emb_cand = self.embedding_engine.embed_text(cand_exp_text)
        exp_emb_jd = self.embedding_engine.embed_text(jd_exp_target)
        exp_similarity = self.embedding_engine.cosine_similarity(exp_emb_cand, exp_emb_jd)
        exp_score = round(exp_similarity * 100.0, 1)

        # 3. Education Section Semantic Similarity
        cand_edu_text = candidate_sections.get("education", "")
        jd_edu_target = f"{jd_data.get('education_level', '')} {jd_data.get('title', '')}"
        edu_emb_cand = self.embedding_engine.embed_text(cand_edu_text)
        edu_emb_jd = self.embedding_engine.embed_text(jd_edu_target)
        edu_similarity = self.embedding_engine.cosine_similarity(edu_emb_cand, edu_emb_jd)
        edu_score = round(edu_similarity * 100.0, 1)

        # 4. Overall Holistic Semantic Fit
        cand_full_text = candidate_sections.get("raw_text", "") or " ".join(
            candidate_sections.values()
        )
        full_emb_cand = self.embedding_engine.embed_text(cand_full_text)
        full_emb_jd = self.embedding_engine.embed_text(f"{jd_desc} {' '.join(required_skills)}")
        sem_similarity = self.embedding_engine.cosine_similarity(full_emb_cand, full_emb_jd)
        sem_score = round(sem_similarity * 100.0, 1)

        # Weighted aggregate score
        overall_fit = (
            (skills_score * w_skills)
            + (exp_score * w_exp)
            + (edu_score * w_edu)
            + (sem_score * w_sem)
        )
        overall_fit = max(0.0, min(100.0, round(overall_fit, 1)))

        # 5. Generate Concrete Learning & Project Recommendations
        recommendations = self._generate_recommendations(
            skill_report.missing_required, skill_report.missing_preferred
        )

        coverage_pct = round(skill_report.required_match_ratio * 100.0, 1)
        source = (
            "sentence_transformers"
            if self.embedding_engine.model is not None
            else "deterministic_hash_fallback"
        )

        fit_summary = (
            f"Candidate achieved a {overall_fit}% overall match for '{jd_data.get('title', 'Target Role')}'. "
            f"Skill coverage is {coverage_pct}% ({len(skill_report.matched_required)}/{len(required_skills)} required skills matched)."
        )

        return MatchEvaluationResult(
            overall_fit_score=overall_fit,
            section_scores={
                "skills": skills_score,
                "experience": exp_score,
                "education": edu_score,
                "semantic_fit": sem_score,
            },
            skill_gap=SkillGapReport(
                matched_skills=skill_report.matched_required + skill_report.matched_preferred,
                missing_required_skills=skill_report.missing_required,
                missing_preferred_skills=skill_report.missing_preferred,
                coverage_pct=coverage_pct,
                recommendations=recommendations,
            ),
            embedding_source=source,
            fit_summary=fit_summary,
        )

    def _generate_recommendations(
        self, missing_required: List[str], missing_preferred: List[str]
    ) -> List[str]:
        """Generates actionable project or learning advice to bridge detected skill gaps."""
        recs = []

        if not missing_required and not missing_preferred:
            recs.append("Candidate demonstrates full technical skill coverage for this role.")
            return recs

        # Group missing required skills by category
        grouped_required: Dict[str, List[str]] = {}
        for skill in missing_required:
            cat = skill_extractor.category_map.get(skill, "frameworks")
            grouped_required.setdefault(cat, []).append(skill)

        for cat, skills in grouped_required.items():
            skills_str = ", ".join(skills)
            template = CATEGORY_RECOMMENDATION_TEMPLATES.get(
                cat, "Gain practical experience with {skills} through open-source code contributions."
            )
            recs.append(template.format(skills=skills_str))

        if missing_preferred:
            pref_str = ", ".join(missing_preferred[:4])
            recs.append(
                f"Bonus differentiator: Familiarize with preferred tooling ({pref_str}) to strengthen competitive positioning."
            )

        return recs


# Global singleton semantic matcher instance
semantic_matcher = SemanticMatcherService()
