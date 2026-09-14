"""Fonte de vagas: Solides.

O endpoint público, quando existe, precisa ser confirmado empresa a
empresa (inspecione a aba Network da página de carreiras no navegador).
Implementação deixada como esqueleto até a validação.
"""

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource


class SolidesSource(JobSource):
    name = "solides"

    def fetch_jobs(self, companies: list[str]) -> list[JobPosting]:
        if companies:
            print(f"[solides] endpoint ainda não validado para: {companies}. "
                  f"Preencha a lógica de fetch em sources/solides.py após inspecionar "
                  f"a aba Network da página de vagas da empresa.")
        return []
