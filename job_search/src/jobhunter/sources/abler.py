"""Fonte de vagas: Abler, por empresa específica (opcional).
Sem agregador público por área — a varredura diária usa Adzuna/Jooble."""

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource


class AblerSource(JobSource):
    name = "abler"

    def __init__(self, companies: list[str] | None = None):
        self.companies = companies or []

    def fetch_jobs(self) -> list[JobPosting]:
        if self.companies:
            print(f"[abler] endpoint ainda não validado para: {self.companies}.")
        return []
