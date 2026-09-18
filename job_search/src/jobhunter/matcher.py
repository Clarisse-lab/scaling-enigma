"""Pontua vagas comparando a descrição com as palavras-chave configuradas
em job_search/config/keywords.yaml.

Matching simples por substring (case-insensitive). Suficiente para uma
primeira triagem; pode evoluir para embeddings/similaridade semântica
depois que houver dados reais suficientes para justificar a complexidade.
"""

from pathlib import Path
from urllib.parse import urlsplit

import yaml

from jobhunter.models import JobPosting

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def _dedupe_key(job: JobPosting) -> tuple:
    if job.url:
        # Ignora querystring (utm_medium/utm_source etc.) pra não tratar a
        # mesma vaga como diferente só por causa de parâmetros de tracking.
        split = urlsplit(job.url)
        return ("url", split.netloc + split.path)
    return ("title_company", job.title.strip().lower(), job.company.strip().lower())


def dedupe_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    """Remove vagas repetidas — a mesma vaga pode aparecer mais de uma vez
    porque consultas diferentes em search.yaml batem no mesmo anúncio."""
    seen = set()
    unique = []
    for job in jobs:
        key = _dedupe_key(job)
        if key in seen:
            continue
        seen.add(key)
        unique.append(job)
    return unique


def load_keywords(path: Path = CONFIG_DIR / "keywords.yaml") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    terms = []
    for category, entries in data.items():
        for entry in entries or []:
            terms.append({"term": entry["term"], "weight": entry["weight"], "category": category})
    return terms


def score_job(job: JobPosting, keywords: list[dict]) -> JobPosting:
    text = f"{job.title}\n{job.description}".lower()
    score = 0.0
    matched = []

    for kw in keywords:
        if kw["term"].lower() in text:
            score += kw["weight"]
            matched.append(kw["term"])

    job.score = score
    job.matched_terms = matched
    return job


def rank_jobs(jobs: list[JobPosting], keywords: list[dict] | None = None) -> list[JobPosting]:
    keywords = keywords or load_keywords()
    scored = [score_job(job, keywords) for job in jobs]
    return sorted(scored, key=lambda j: j.score, reverse=True)
