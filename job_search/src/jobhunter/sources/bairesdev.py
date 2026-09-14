"""Fonte de vagas: BairesDev, por empresa específica (opcional).
Sem agregador público por área — a varredura diária usa Adzuna/Jooble."""

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource


class BairesDevSource(JobSource):
    name = "bairesdev"

    def __init__(self, companies: list[str] | None = None):
        self.companies = companies or []

    def fetch_jobs(self) -> list[JobPosting]:
        if self.companies:
            print(f"[bairesdev] endpoint ainda não validado para: {self.companies}.")
        return []
