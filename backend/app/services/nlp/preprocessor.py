import re
import unicodedata
from typing import List, Set
from pydantic import BaseModel, Field

# Protected technical terms that must NOT be aggressively split or stripped
PROTECTED_TECH_TERMS = {
    "c++",
    "c#",
    ".net",
    "asp.net",
    "node.js",
    "next.js",
    "vue.js",
    "react.js",
    "nuxt.js",
    "nest.js",
    "three.js",
    "d3.js",
    "express.js",
    "angular.js",
    "ai/ml",
    "ci/cd",
    "tcp/ip",
    "rest/graphql",
    "pl/sql",
    "t-sql",
    "scikit-learn",
    "power bi",
    "f#",
    "r",
    "go",
    "objective-c",
    "sql/nosql",
    "onnx runtime",
    "hugging face",
}

# Standard English stopwords fallback
DEFAULT_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

# Suffixes for basic morphological lemmatizer fallback
LEMMA_SUFFIX_RULES = [
    ("sses", "ss"),
    ("ies", "y"),
    ("eed", "ee"),
    ("ed", ""),
    ("ing", ""),
    ("izer", "ize"),
    ("izes", "ize"),
    ("ized", "ize"),
    ("ation", "ate"),
    ("ations", "ate"),
    ("abilities", "ability"),
    ("ities", "ity"),
    ("s", ""),
]


class PreprocessedOutput(BaseModel):
    normalized_text: str
    tokens: List[str]
    filtered_tokens: List[str]
    lemmatized_tokens: List[str]
    preserved_tech_terms: List[str] = Field(default_factory=list)


class NLPPreprocessorService:
    """
    Normalizes textual artifacts, cleans noisy formatting, extracts tokens while protecting
    domain-critical technology terms (e.g. C++, .NET, CI/CD, Node.js), and applies lemmatization.
    """

    def __init__(self):
        self._stopwords = self._init_stopwords()
        self._lemmatizer = self._init_lemmatizer()

    def _init_stopwords(self) -> Set[str]:
        try:
            from nltk.corpus import stopwords

            words = set(stopwords.words("english"))
            # Ensure protected tech terms are NEVER filtered as stopwords
            for term in PROTECTED_TECH_TERMS:
                words.discard(term)
                words.discard(term.lower())
            return words
        except Exception:
            return set(DEFAULT_STOPWORDS)

    def _init_lemmatizer(self):
        try:
            from nltk.stem import WordNetLemmatizer

            lemmatizer = WordNetLemmatizer()
            # Test if WordNet is downloaded
            lemmatizer.lemmatize("testing")
            return lemmatizer
        except Exception:
            return None

    def clean_text(self, text: str) -> str:
        """
        Removes noisy Unicode artifacts, smart quotes, bullet marks, and unified linebreaks.
        """
        if not text:
            return ""

        # Normalize unicode (NFKC)
        text = unicodedata.normalize("NFKC", text)

        # Replace smart quotes and special typographical marks
        text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        text = text.replace("–", "-").replace("—", "-").replace("…", "...")
        text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219▪•◆*]", " ", text)  # Bullet characters

        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()

    def tokenize(self, text: str) -> tuple[List[str], List[str]]:
        """
        Extracts tokens while preserving compound technical keywords.
        Returns (tokens, preserved_tech_terms).
        """
        if not text:
            return [], []

        cleaned = self.clean_text(text)
        lowered = cleaned.lower()

        # Step 1: Detect and mask protected tech terms
        preserved_found: List[str] = []
        placeholder_map = {}

        # Sort protected terms by length descending to match longest first (e.g. asp.net before .net)
        sorted_terms = sorted(PROTECTED_TECH_TERMS, key=len, reverse=True)

        masked_text = lowered
        for i, term in enumerate(sorted_terms):
            pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
            if re.search(pattern, masked_text):
                placeholder = f"__PROTECTED_TECH_{i}__"
                placeholder_map[placeholder] = term
                preserved_found.append(term)
                masked_text = re.sub(pattern, f" {placeholder} ", masked_text)

        # Step 2: Split remaining alphanumeric words
        raw_tokens = re.findall(r"[A-Za-z0-9_#+.-]+|\S", masked_text)

        # Step 3: Unmask placeholders
        final_tokens: List[str] = []
        for t in raw_tokens:
            cleaned_t = t.strip(".,;:()[]{}\"'")
            if not cleaned_t:
                continue

            if cleaned_t in placeholder_map:
                final_tokens.append(placeholder_map[cleaned_t])
            elif cleaned_t in PROTECTED_TECH_TERMS:
                final_tokens.append(cleaned_t)
            else:
                # Remove purely punctuation tokens
                if re.match(r"^[^\w]+$", cleaned_t) and cleaned_t not in {"c++", "c#"}:
                    continue
                final_tokens.append(cleaned_t)

        return final_tokens, preserved_found

    def filter_stopwords(self, tokens: List[str]) -> List[str]:
        """Filters out non-technical English stopwords."""
        filtered = []
        for token in tokens:
            t_lower = token.lower()
            if t_lower in PROTECTED_TECH_TERMS:
                filtered.append(token)
            elif t_lower not in self._stopwords and len(token) > 1:
                filtered.append(token)
        return filtered

    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatizes tokens to root form while strictly keeping tech terms intact.
        """
        lemmatized = []
        for token in tokens:
            t_lower = token.lower()
            if t_lower in PROTECTED_TECH_TERMS:
                lemmatized.append(token)
            elif self._lemmatizer is not None:
                try:
                    lemmatized.append(self._lemmatizer.lemmatize(token))
                except Exception:
                    lemmatized.append(self._rule_based_lemma(token))
            else:
                lemmatized.append(self._rule_based_lemma(token))
        return lemmatized

    def _rule_based_lemma(self, word: str) -> str:
        """Deterministic morphological stemming/lemmatization fallback."""
        w = word.lower()
        if len(w) <= 3:
            return word

        for suffix, replacement in LEMMA_SUFFIX_RULES:
            if w.endswith(suffix) and len(w) > len(suffix) + 2:
                return w[: -len(suffix)] + replacement
        return word

    def preprocess(self, text: str) -> PreprocessedOutput:
        """Full end-to-end NLP preprocessing pipeline."""
        normalized = self.clean_text(text)
        tokens, preserved = self.tokenize(normalized)
        filtered = self.filter_stopwords(tokens)
        lemmas = self.lemmatize(filtered)

        return PreprocessedOutput(
            normalized_text=normalized,
            tokens=tokens,
            filtered_tokens=filtered,
            lemmatized_tokens=lemmas,
            preserved_tech_terms=preserved,
        )


# Global singleton preprocessor instance
nlp_preprocessor = NLPPreprocessorService()
