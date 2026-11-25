import datetime
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

# Canonical Skill Taxonomy categorized by discipline
TAXONOMY_CATEGORIES = {
    "languages": [
        "Python", "JavaScript", "TypeScript", "C++", "C#", "Java", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "SQL", "HTML5", "CSS3",
        "Bash", "Shell", "Dart", "Elixir", "Haskell", "Julia", "MATLAB"
    ],
    "frameworks": [
        "React", "Next.js", "Vue.js", "Angular", "FastAPI", "Flask", "Django",
        "Express", "Spring Boot", "Node.js", "PyTorch", "TensorFlow", "Keras",
        "Scikit-Learn", "Whisper", "LangChain", "Transformers", "Hugging Face",
        "Redux", "Tailwind CSS", "Bootstrap", "GraphQL", "REST APIs", "gRPC",
        "Pandas", "NumPy", "OpenCV", "ONNX Runtime", "LlamaIndex"
    ],
    "databases": [
        "MongoDB", "PostgreSQL", "MySQL", "Redis", "DynamoDB", "Cassandra",
        "Elasticsearch", "Pinecone", "ChromaDB", "Milvus", "Weaviate",
        "Snowflake", "BigQuery", "SQLite", "Neo4j", "Oracle", "Supabase"
    ],
    "cloud_devops": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
        "Helm", "GitHub Actions", "GitLab CI", "CI/CD", "Jenkins", "Linux",
        "Nginx", "Apache", "Kafka", "RabbitMQ", "Prometheus", "Grafana"
    ],
    "ai_ml": [
        "NLP", "Computer Vision", "Speech-to-Text", "ASR", "LLM", "Generative AI",
        "Vector Embeddings", "Vector Search", "Prompt Engineering", "Sentiment Analysis",
        "RAG", "Deep Learning", "Machine Learning", "Data Science", "MLOps",
        "Model Distillation", "Fine-Tuning", "Reinforcement Learning"
    ],
    "methodologies_domains": [
        "Agile", "Scrum", "Microservices", "System Design", "TDD", "Clean Architecture",
        "Distributed Systems", "Multimodal", "Object-Oriented Programming",
        "Event-Driven Architecture", "ETL", "Data Pipelines"
    ],
}

# Aliases and variations to canonical forms
SKILL_ALIASES = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "nodejs": "Node.js",
    "node": "Node.js",
    "node.js": "Node.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angularjs": "Angular",
    "angular": "Angular",
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    "kubernetes": "Kubernetes",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "py": "Python",
    "python": "Python",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "golang": "Go",
    "go": "Go",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "fastapi": "FastAPI",
    "whisper": "Whisper",
    "whisper asr": "Whisper",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "llm": "LLM",
    "large language models": "LLM",
    "rag": "RAG",
    "retrieval-augmented generation": "RAG",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful apis": "REST APIs",
    "docker": "Docker",
    "git": "GitHub Actions",
}

# Regex for experience years extraction
EXP_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:professional\s+)?experience)?", re.IGNORECASE),
    re.compile(r"(?:experience|track record)\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*years?", re.IGNORECASE),
    re.compile(r"(?:over|more than)\s+(\d+(?:\.\d+)?)\s+years?", re.IGNORECASE),
]

# Regex for education levels
EDUCATION_PATTERNS = {
    "Ph.D. / Doctorate": re.compile(r"\b(?:ph\.?d|doctorate|doctor of philosophy)\b", re.IGNORECASE),
    "Master's Degree": re.compile(r"\b(?:master(?:'s)?(?:\s+of\s+science)?|m\.?s\.?|m\.?tech|mca|mba)\b", re.IGNORECASE),
    "Bachelor's Degree": re.compile(r"\b(?:bachelor(?:'s)?(?:\s+of\s+science)?|b\.?s\.?|b\.?tech|b\.?e\.?|bca|b\.?a\.?)\b", re.IGNORECASE),
    "Associate / Diploma": re.compile(r"\b(?:associate(?:'s)?(?:\s+degree)?|diploma)\b", re.IGNORECASE),
}


class ExtractedSkillsResult(BaseModel):
    skills_by_category: Dict[str, List[str]]
    all_skills: List[str]
    normalized_skills: List[str]
    experience_years_detected: Optional[float] = None
    education_degrees_detected: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    skill_occurrences: Dict[str, int] = Field(default_factory=dict)


class SkillMatchReport(BaseModel):
    matched_required: List[str]
    missing_required: List[str]
    matched_preferred: List[str]
    missing_preferred: List[str] = Field(default_factory=list)
    additional_candidate_skills: List[str]
    required_match_ratio: float = Field(..., ge=0.0, le=1.0)
    preferred_match_ratio: float = Field(..., ge=0.0, le=1.0)
    overall_skill_score: float = Field(..., ge=0.0, le=100.0)


class SkillExtractorService:
    """
    Extracts canonical technical skills, frameworks, tools, experience tenure signals,
    and degree levels from candidate resumes, video transcripts, and job descriptions.
    """

    def __init__(self):
        self.canonical_map: Dict[str, str] = {}
        self.category_map: Dict[str, str] = {}
        self._build_lookup_index()

    def _build_lookup_index(self):
        """Builds lookup index from taxonomy and alias maps."""
        for category, skills in TAXONOMY_CATEGORIES.items():
            for skill in skills:
                lower = skill.lower()
                self.canonical_map[lower] = skill
                self.category_map[skill] = category

        # Add explicit aliases
        for alias, canonical in SKILL_ALIASES.items():
            self.canonical_map[alias.lower()] = canonical

    def extract_skills(self, text: str) -> ExtractedSkillsResult:
        """
        Extracts all canonical skills, frequencies, experience, and education signals from text.
        """
        if not text:
            return ExtractedSkillsResult(
                skills_by_category={cat: [] for cat in TAXONOMY_CATEGORIES},
                all_skills=[],
                normalized_skills=[],
                experience_years_detected=None,
                education_degrees_detected=[],
            )

        occurrences: Dict[str, int] = {}
        text_lower = f" {text.lower()} "

        # Scan for canonical terms and aliases
        # Sort keys by descending length so multi-word terms (e.g. "speech-to-text", "vector embeddings")
        # take precedence over single words
        sorted_keys = sorted(self.canonical_map.keys(), key=len, reverse=True)

        found_canonical: Set[str] = set()

        for term in sorted_keys:
            canonical = self.canonical_map[term]

            # Use word boundaries or specialized anchors for punctuation terms (C++, C#, .NET)
            if term in ["c++", "c#", ".net", "ai/ml", "ci/cd"]:
                pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
            elif len(term) <= 2:
                # Short keywords like 'r', 'go' require strict word boundaries and case checks
                pattern = rf"\b{re.escape(term)}\b"
                if term in ["r", "go"]:
                    # Must be capitalized in original text or in tech context
                    if not re.search(rf"\b{term.upper()}\b|\bGo\b", text):
                        continue
            else:
                pattern = rf"\b{re.escape(term)}\b"

            matches = re.findall(pattern, text_lower)
            if matches:
                occurrences[canonical] = occurrences.get(canonical, 0) + len(matches)
                found_canonical.add(canonical)

        # Categorize detected skills
        by_category: Dict[str, List[str]] = {cat: [] for cat in TAXONOMY_CATEGORIES}
        for skill in found_canonical:
            cat = self.category_map.get(skill, "frameworks")
            by_category[cat].append(skill)

        # Sort skills for deterministic order
        for cat in by_category:
            by_category[cat].sort()
        all_skills_list = sorted(list(found_canonical))

        # Detect experience years
        exp_years = self._extract_experience_years(text)

        # Detect education degrees
        degrees = self._extract_education_degrees(text)

        return ExtractedSkillsResult(
            skills_by_category=by_category,
            all_skills=all_skills_list,
            normalized_skills=all_skills_list,
            experience_years_detected=exp_years,
            education_degrees_detected=degrees,
            confidence_score=94.0 if all_skills_list else 80.0,
            skill_occurrences=occurrences,
        )

    def _extract_experience_years(self, text: str) -> Optional[float]:
        """Detects years of experience mentioned in resume summary or calculated from dates."""
        # 1. Direct explicit phrases e.g. "5+ years of experience"
        candidates = []
        for pattern in EXP_PATTERNS:
            for match in pattern.finditer(text):
                try:
                    val = float(match.group(1))
                    if 0.5 <= val <= 35.0:
                        candidates.append(val)
                except (ValueError, IndexError):
                    pass

        if candidates:
            # Return max stated experience
            return max(candidates)

        # 2. Date range heuristics: e.g. "2019 - 2024" or "2018 - Present"
        date_pattern = re.compile(
            r"\b(20\d\d|19\d\d)\s*(?:-|to|–)\s*(20\d\d|present|current)\b", re.IGNORECASE
        )
        current_year = datetime.datetime.now().year
        total_span = 0.0

        for match in date_pattern.finditer(text):
            try:
                start_year = int(match.group(1))
                end_str = match.group(2).lower()
                end_year = current_year if "present" in end_str or "current" in end_str else int(end_str)
                if 1980 <= start_year <= current_year and end_year >= start_year:
                    diff = end_year - start_year
                    total_span = max(total_span, float(diff))
            except Exception:
                pass

        return total_span if total_span > 0 else None

    def _extract_education_degrees(self, text: str) -> List[str]:
        """Detects highest educational degree mentions."""
        detected = []
        for degree_name, pattern in EDUCATION_PATTERNS.items():
            if pattern.search(text):
                detected.append(degree_name)
        return detected

    def match_skills(
        self,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None,
    ) -> SkillMatchReport:
        """
        Calculates exact overlap, missing skills, and weighted fit scores against Job Description criteria.
        """
        preferred_skills = preferred_skills or []

        # Normalize all inputs via alias mapping
        norm_cand = {self.canonical_map.get(s.lower(), s) for s in candidate_skills}
        norm_req = {self.canonical_map.get(s.lower(), s) for s in required_skills}
        norm_pref = {self.canonical_map.get(s.lower(), s) for s in preferred_skills}

        matched_req = sorted(list(norm_cand.intersection(norm_req)))
        missing_req = sorted(list(norm_req.difference(norm_cand)))
        matched_pref = sorted(list(norm_cand.intersection(norm_pref)))
        missing_pref = sorted(list(norm_pref.difference(norm_cand)))
        additional = sorted(list(norm_cand.difference(norm_req).difference(norm_pref)))

        req_ratio = len(matched_req) / max(len(norm_req), 1)
        pref_ratio = len(matched_pref) / max(len(norm_pref), 1) if norm_pref else 1.0

        # Overall skill score calculation: 75% required weight + 25% preferred weight
        if norm_pref:
            overall_score = round((req_ratio * 75.0) + (pref_ratio * 25.0), 1)
        else:
            overall_score = round(req_ratio * 100.0, 1)

        return SkillMatchReport(
            matched_required=matched_req,
            missing_required=missing_req,
            matched_preferred=matched_pref,
            missing_preferred=missing_pref,
            additional_candidate_skills=additional,
            required_match_ratio=round(req_ratio, 3),
            preferred_match_ratio=round(pref_ratio, 3),
            overall_skill_score=overall_score,
        )


# Global singleton skill extractor instance
skill_extractor = SkillExtractorService()
