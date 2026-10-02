"""
Text cleaning and simple NLP helpers used across analyzers.
"""

import re
from typing import Optional


def sanitize_text(text: str) -> str:
    """Normalize whitespace and strip control characters from extracted text."""
    if not text:
        return ""
    # Remove null bytes and most control chars (keep newlines/tabs)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    # Normalize line endings
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse excessive blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Collapse multiple spaces (but keep newlines)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def normalize_for_match(text: str) -> str:
    """Lowercase text for case-insensitive matching."""
    return (text or "").lower()


def extract_email(text: str) -> Optional[str]:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    # Common Indian / international phone patterns
    patterns = [
        r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,5}[\s\-]?\d{4,6}",
        r"(?:\+91[\s\-]?)?[6-9]\d{9}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(0).strip()
            digits = re.sub(r"\D", "", candidate)
            if 10 <= len(digits) <= 15:
                return candidate
    return None


def extract_url(text: str, domain_hint: str) -> Optional[str]:
    pattern = rf"(https?://)?(www\.)?{re.escape(domain_hint)}[^\s\)\],]*"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0).rstrip(".,;")
    # Also catch bare handles like linkedin.com/in/name
    bare = re.search(rf"{re.escape(domain_hint)}/[^\s\)\],]+", text, re.IGNORECASE)
    return bare.group(0) if bare else None


def find_section_block(text: str, headings: list[str]) -> str:
    """
    Extract text under a section heading until the next known heading.
    """
    lower = text.lower()
    all_headings = [
        "summary", "objective", "profile", "about me",
        "education", "academic",
        "experience", "work experience", "employment", "professional experience",
        "projects", "personal projects", "academic projects",
        "skills", "technical skills", "technologies", "tech stack",
        "certifications", "certificates", "licenses",
        "achievements", "accomplishments", "awards",
        "languages", "interests", "hobbies", "references",
    ]

    start_idx = -1
    matched_heading = ""
    for h in headings:
        idx = lower.find(h.lower())
        if idx != -1 and (start_idx == -1 or idx < start_idx):
            start_idx = idx
            matched_heading = h.lower()

    if start_idx == -1:
        return ""

    # Find end: next heading after start
    search_from = start_idx + len(matched_heading)
    end_idx = len(text)
    for h in all_headings:
        if h == matched_heading:
            continue
        # Prefer headings that appear near the start of a line
        for m in re.finditer(rf"(?m)^\s*{re.escape(h)}\b", lower[search_from:]):
            candidate = search_from + m.start()
            if candidate < end_idx:
                end_idx = candidate
            break

    return text[start_idx:end_idx].strip()


def split_lines(block: str) -> list[str]:
    return [ln.strip(" •-\t") for ln in block.split("\n") if ln.strip()]


ACTION_VERBS = {
    "built", "created", "developed", "designed", "implemented", "improved",
    "led", "managed", "optimized", "automated", "analyzed", "delivered",
    "engineered", "architected", "integrated", "deployed", "tested",
    "collaborated", "reduced", "increased", "achieved", "launched",
    "maintained", "refactored", "configured", "documented", "mentored",
}


def has_action_verb(text: str) -> bool:
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    return bool(words & ACTION_VERBS)


def has_quantifiable(text: str) -> bool:
    return bool(re.search(r"\d+%|\d+\+|\$\d+|\d+\s*(users|clients|projects|tests|apis|features)", text, re.I))
