"""Fonte de vagas: BairesDev. Endpoint a validar (ver solides.py para o
motivo). Esqueleto até a validação."""

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource


class BairesDevSource(JobSource):
    name = "bairesdev"

    def fetch_jobs(self, companies: list[str]) -> list[JobPosting]:
        if companies:
            print(f"[bairesdev] endpoint ainda não validado para: {companies}.")
        return []
