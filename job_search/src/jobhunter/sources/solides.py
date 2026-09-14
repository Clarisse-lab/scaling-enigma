"""Fonte de vagas: Solides, por empresa específica (opcional).

Sem agregador público por área — a varredura diária usa Adzuna/Jooble.
Endpoint ainda não validado; preencher após inspecionar a aba Network da
página de vagas da empresa.
"""

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource


class SolidesSource(JobSource):
    name = "solides"

    def __init__(self, companies: list[str] | None = None):
        self.companies = companies or []

    def fetch_jobs(self) -> list[JobPosting]:
        if self.companies:
            print(f"[solides] endpoint ainda não validado para: {self.companies}.")
        return []
