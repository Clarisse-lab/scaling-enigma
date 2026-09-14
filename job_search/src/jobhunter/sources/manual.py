"""Fonte de vagas: entradas manuais (LinkedIn, Glassdoor, indicações).

Lê job_search/config/manual_jobs.yaml, onde você cola vagas encontradas
em plataformas que não automatizamos por risco de violar os Termos de
Uso (scraping de LinkedIn/Glassdoor).
"""

from pathlib import Path

import yaml

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "manual_jobs.yaml"


class ManualSource(JobSource):
    name = "manual"

    def fetch_jobs(self, companies: list[str] | None = None) -> list[JobPosting]:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []

        return [
            JobPosting(
                title=entry.get("title", ""),
                company=entry.get("company", ""),
                url=entry.get("url", ""),
                source=entry.get("source", "manual"),
                description=entry.get("description", ""),
            )
            for entry in entries
        ]
