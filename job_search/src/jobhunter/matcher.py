"""Pontua vagas comparando a descrição com as palavras-chave configuradas
em job_search/config/keywords.yaml.

Matching simples por substring (case-insensitive). Suficiente para uma
primeira triagem; pode evoluir para embeddings/similaridade semântica
depois que houver dados reais suficientes para justificar a complexidade.
"""

from pathlib import Path

import yaml

from jobhunter.models import JobPosting

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


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
