import io
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ParsedContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class ResumeSections(BaseModel):
    summary: str = ""
    skills: str = ""
    experience_projects: str = ""
    education: str = ""
    certifications: str = ""
    other: str = ""


class ParsedResume(BaseModel):
    contact_info: ParsedContactInfo
    sections: ResumeSections
    raw_text: str
    file_type: str
    anonymized_text: Optional[str] = None


# Common Section Heading Regexes
HEADING_PATTERNS = {
    "summary": re.compile(
        r"^(?:professional\s+)?(?:summary|profile|about\s+me|objective|overview)\b",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^(?:technical\s+|core\s+)?(?:skills|competencies|technologies|tools\s+&\s+technologies|tech\s+stack)\b",
        re.IGNORECASE,
    ),
    "experience_projects": re.compile(
        r"^(?:work\s+|professional\s+)?(?:experience|employment(?:\s+history)?|work\s+history|projects|key\s+projects)\b",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"^(?:education|academic\s+background|qualifications|academic\s+history)\b",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^(?:certifications|licenses|courses|awards|achievements)\b",
        re.IGNORECASE,
    ),
}

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(
    r"(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}|\b\d{10}\b)"
)
LINKEDIN_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/[A-Za-z0-9_-]+",
    re.IGNORECASE,
)
GITHUB_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?github\.com\/[A-Za-z0-9_-]+",
    re.IGNORECASE,
)
PORTFOLIO_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?[A-Za-z0-9_-]+\.(?:dev|me|io|portfolio|com)\b",
    re.IGNORECASE,
)
LOCATION_REGEX = re.compile(
    r"\b([A-Z][a-zA-Z .\t-]+,[ \t]*(?:[A-Z]{2}|[A-Z][a-zA-Z \t]+))\b"
)


class ResumeParserService:
    """
    Parses PDF, DOCX, TXT, and Markdown resumes into structured sections,
    extracts contact info, and enables robust PII anonymization for bias-free screening.
    """

    def parse(
        self,
        file_input: Union[str, Path, bytes],
        filename: Optional[str] = None,
    ) -> ParsedResume:
        """Main entry point to parse a resume from a file path or raw bytes."""
        raw_text, detected_type = self._extract_raw_text(file_input, filename)
        cleaned_text = self._clean_text(raw_text)

        contact_info = self._extract_contact_info(cleaned_text)
        sections = self._segment_sections(cleaned_text)
        anonymized = self.anonymize_text(cleaned_text, contact_info)

        return ParsedResume(
            contact_info=contact_info,
            sections=sections,
            raw_text=cleaned_text,
            file_type=detected_type,
            anonymized_text=anonymized,
        )

    def _extract_raw_text(
        self,
        file_input: Union[str, Path, bytes],
        filename: Optional[str] = None,
    ) -> tuple[str, str]:
        """Extract text across supported formats: PDF, DOCX, TXT, MD."""
        # Determine filename and raw bytes
        if isinstance(file_input, (str, Path)):
            path = Path(file_input)
            filename = filename or path.name
            with open(path, "rb") as f:
                content = f.read()
        else:
            content = file_input
            filename = filename or "resume.txt"

        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            text = self._extract_pdf(content)
            return text, "pdf"
        elif ext in [".docx", ".doc"]:
            text = self._extract_docx(content)
            return text, "docx"
        else:
            # Plain text / Markdown fallback
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("latin-1", errors="replace")
            return text, "txt"

    def _extract_pdf(self, content: bytes) -> str:
        """Attempts PyMuPDF (fitz) or pdfplumber, falling back to pypdf."""
        # 1. Try PyMuPDF (fitz)
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=content, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            if text.strip():
                return text
        except ImportError:
            pass

        # 2. Try pdfplumber
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                if text.strip():
                    return text
        except ImportError:
            pass

        # 3. Try pypdf
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                return text
        except Exception:
            pass

        # 4. Fallback: string scan
        return content.decode("utf-8", errors="replace")

    def _extract_docx(self, content: bytes) -> str:
        """Attempts python-docx, falling back to XML zip extraction."""
        # 1. Try python-docx
        try:
            import docx

            doc = docx.Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            tables = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        tables.append(row_text)
            return "\n".join(paragraphs + tables)
        except Exception:
            pass

        # 2. Resilient fallback: parse word/document.xml directly from docx zip
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                xml_content = z.read("word/document.xml")
                root = ET.fromstring(xml_content)
                texts = []
                for node in root.iter():
                    if node.tag.endswith("t") and node.text:
                        texts.append(node.text)
                return " ".join(texts)
        except Exception:
            return content.decode("utf-8", errors="replace")

    def _clean_text(self, text: str) -> str:
        """Removes control chars, normalizes non-breaking spaces, and unifies linefeeds."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\u00a0", " ").replace("\u200b", "")
        # Remove consecutive whitespace while preserving line structure
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _extract_contact_info(self, text: str) -> ParsedContactInfo:
        """Extracts PII fields: name, email, phone, location, LinkedIn, GitHub, portfolio."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Email
        emails = EMAIL_REGEX.findall(text)
        email = emails[0] if emails else None

        # 2. Phone
        phones = PHONE_REGEX.findall(text)
        phone = None
        for p in phones:
            cleaned_p = re.sub(r"[^\d+]", "", p)
            if 7 <= len(cleaned_p) <= 15:
                phone = p.strip()
                break

        # 3. LinkedIn
        linkedin_matches = LINKEDIN_REGEX.findall(text)
        linkedin = linkedin_matches[0] if linkedin_matches else None

        # 4. GitHub
        github_matches = GITHUB_REGEX.findall(text)
        github = github_matches[0] if github_matches else None

        # 5. Portfolio
        portfolio = None
        portfolio_candidates = PORTFOLIO_REGEX.findall(text)
        for url in portfolio_candidates:
            if "linkedin.com" not in url and "github.com" not in url and (email and email not in url):
                portfolio = url
                break

        # 6. Candidate Name heuristic (first 1-3 lines usually contain full name)
        name = None
        for line in lines[:4]:
            if line and not EMAIL_REGEX.search(line) and not PHONE_REGEX.search(line):
                cleaned_line = re.sub(r"[\(\)\|•,]", "", line).strip()
                words = cleaned_line.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                    name = " ".join(words)
                    break

        # 7. Location heuristic (e.g. San Francisco, CA)
        location = None
        loc_match = LOCATION_REGEX.search(text[:600])
        if loc_match:
            location = loc_match.group(1).strip()

        return ParsedContactInfo(
            name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin,
            github_url=github,
            portfolio_url=portfolio,
        )

    def _segment_sections(self, text: str) -> ResumeSections:
        """Segments resume into summary, skills, experience_projects, education, certifications."""
        lines = text.split("\n")
        sections_data: Dict[str, List[str]] = {
            "summary": [],
            "skills": [],
            "experience_projects": [],
            "education": [],
            "certifications": [],
            "other": [],
        }

        current_section = "other"

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check if this line is a section header (short uppercase/titlecase line)
            is_header = False
            if len(line_str.split()) <= 5:
                for sec_key, pattern in HEADING_PATTERNS.items():
                    if pattern.match(line_str):
                        current_section = sec_key
                        is_header = True
                        break

            if not is_header:
                sections_data[current_section].append(line_str)

        return ResumeSections(
            summary="\n".join(sections_data["summary"]).strip(),
            skills="\n".join(sections_data["skills"]).strip(),
            experience_projects="\n".join(sections_data["experience_projects"]).strip(),
            education="\n".join(sections_data["education"]).strip(),
            certifications="\n".join(sections_data["certifications"]).strip(),
            other="\n".join(sections_data["other"]).strip(),
        )

    def anonymize_text(self, text: str, contact_info: ParsedContactInfo) -> str:
        """
        Redacts personally identifiable information (PII) to produce an anonymized view
        for bias-free candidate evaluation.
        """
        sanitized = text

        # 1. Redact emails first so name parts within email addresses do not break regex matching
        if contact_info.email:
            sanitized = sanitized.replace(contact_info.email, "[EMAIL_REDACTED]")
        sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", sanitized)

        # 2. Redact phones
        if contact_info.phone:
            sanitized = sanitized.replace(contact_info.phone, "[PHONE_REDACTED]")
        sanitized = PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)

        # 3. Redact social and portfolio links
        if contact_info.linkedin_url:
            sanitized = sanitized.replace(contact_info.linkedin_url, "[LINKEDIN_REDACTED]")
        sanitized = LINKEDIN_REGEX.sub("[LINKEDIN_REDACTED]", sanitized)

        if contact_info.github_url:
            sanitized = sanitized.replace(contact_info.github_url, "[GITHUB_REDACTED]")
        sanitized = GITHUB_REGEX.sub("[GITHUB_REDACTED]", sanitized)

        # 4. Redact location
        if contact_info.location:
            sanitized = sanitized.replace(contact_info.location, "[LOCATION_REDACTED]")

        # 5. Redact full name and individual name parts
        if contact_info.name:
            sanitized = re.sub(
                re.escape(contact_info.name), "[CANDIDATE_NAME]", sanitized, flags=re.IGNORECASE
            )
            for part in contact_info.name.split():
                if len(part) > 2:
                    sanitized = re.sub(
                        rf"\b{re.escape(part)}\b", "[NAME_PART]", sanitized, flags=re.IGNORECASE
                    )

        return sanitized


# Global singleton parser instance
resume_parser = ResumeParserService()
