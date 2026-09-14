from dataclasses import dataclass, field


@dataclass
class JobPosting:
    title: str
    company: str
    url: str
    source: str
    description: str = ""
    location: str = ""
    score: float = 0.0
    matched_terms: list[str] = field(default_factory=list)
