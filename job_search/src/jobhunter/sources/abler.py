"""Fonte de vagas: Abler. Endpoint a validar por empresa (ver solides.py
para o motivo). Esqueleto até a validação."""

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource


class AblerSource(JobSource):
    name = "abler"

    def fetch_jobs(self, companies: list[str]) -> list[JobPosting]:
        if companies:
            print(f"[abler] endpoint ainda não validado para: {companies}.")
        return []
