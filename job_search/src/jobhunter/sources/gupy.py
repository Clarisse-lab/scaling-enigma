"""Fonte de vagas: Gupy, por empresa específica.

Gupy não tem um agregador público de busca por área entre todas as
empresas — cada empresa tem seu próprio painel. Esta fonte só entra em
ação se você configurar `companies` em job_search/config/platforms.yaml;
a varredura diária por área usa Adzuna/Jooble (ver adzuna.py, jooble.py).

O endpoint abaixo é o padrão mais comum observado em painéis Gupy, mas
PRECISA ser confirmado por empresa (abra a página da empresa no navegador,
aba Network, e copie a URL do request que retorna a lista de vagas em
JSON) antes de confiar cegamente nele.
"""

import requests

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource

JOB_BOARD_URL_TEMPLATE = "https://{company}.gupy.io/api/job_postings/published"


class GupySource(JobSource):
    name = "gupy"

    def __init__(self, companies: list[str] | None = None):
        self.companies = companies or []

    def fetch_jobs(self) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        for company in self.companies:
            url = JOB_BOARD_URL_TEMPLATE.format(company=company)
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                payload = resp.json()
            except (requests.RequestException, ValueError) as exc:
                print(f"[gupy] falha ao buscar vagas de '{company}': {exc}. "
                      f"Confirme o endpoint real no navegador (aba Network).")
                continue

            for item in payload.get("data", []):
                jobs.append(JobPosting(
                    title=item.get("name", ""),
                    company=company,
                    url=item.get("jobUrl", url),
                    source=self.name,
                    description=item.get("description", ""),
                    location=item.get("city", ""),
                ))
        return jobs
