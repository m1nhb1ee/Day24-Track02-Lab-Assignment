import re
from dataclasses import dataclass

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
CCCD_RE = re.compile(r"\b\d{12}\b")
PHONE_RE = re.compile(r"\b0[35789]\d{8}\b")
NAME_RE = re.compile(r"\b[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,4}\b")


@dataclass
class SimpleResult:
    entity_type: str
    start: int
    end: int
    score: float = 1.0


class SimpleAnalyzer:
    def analyze(self, text: str, language: str = "vi", entities=None):
        entities = set(entities or [])
        results = []

        if not entities or "EMAIL_ADDRESS" in entities:
            for m in EMAIL_RE.finditer(text):
                results.append(SimpleResult("EMAIL_ADDRESS", m.start(), m.end(), 0.95))

        if not entities or "VN_CCCD" in entities:
            for m in CCCD_RE.finditer(text):
                results.append(SimpleResult("VN_CCCD", m.start(), m.end(), 0.95))

        if not entities or "VN_PHONE" in entities:
            for m in PHONE_RE.finditer(text):
                results.append(SimpleResult("VN_PHONE", m.start(), m.end(), 0.9))

        if not entities or "VN_PERSON" in entities or "PERSON" in entities:
            for m in NAME_RE.finditer(text):
                results.append(SimpleResult("VN_PERSON", m.start(), m.end(), 0.7))

        results.sort(key=lambda x: x.start)
        return results


def build_vietnamese_analyzer() -> SimpleAnalyzer:
    return SimpleAnalyzer()


def detect_pii(text: str, analyzer: SimpleAnalyzer) -> list:
    return analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "VN_PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
