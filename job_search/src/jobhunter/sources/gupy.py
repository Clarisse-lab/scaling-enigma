"""Fonte de vagas: Gupy.

Muitas empresas que usam a Gupy expõem um painel público de vagas em
`https://<empresa>.gupy.io`, que carrega os dados via uma API JSON.
O endpoint exato varia por empresa/versão do painel e PRECISA ser
confirmado manualmente antes de automatizar (abra a página da empresa
no navegador, inspecione a aba Network e copie a URL do request que
retorna a lista de vagas em JSON).

Este módulo fica com uma implementação best-effort: tenta o padrão mais
comum e falha de forma explícita se a resposta não for a esperada, em vez
de mascarar o erro.
"""

import requests

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource

# Padrão observado com mais frequência; validar por empresa antes de confiar.
JOB_BOARD_URL_TEMPLATE = "https://{company}.gupy.io/api/job_postings/published"


class GupySource(JobSource):
    name = "gupy"

    def fetch_jobs(self, companies: list[str]) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        for company in companies:
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
