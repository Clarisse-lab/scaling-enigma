"""Fonte de vagas: Adzuna — agregador com API pública de busca por
palavra-chave/localização (não precisa saber a empresa antes).

Requer conta gratuita em https://developer.adzuna.com/ para obter
`app_id` e `app_key`, passados via variáveis de ambiente:
    ADZUNA_APP_ID, ADZUNA_APP_KEY

Endpoint documentado: GET
https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
    ?app_id=...&app_key=...&what=...&where=...&results_per_page=...&content-type=application/json

`country` usa o código de duas letras (Brasil = "br"). Não foi possível
testar ao vivo a partir deste ambiente de desenvolvimento (sem acesso à
internet aberta) — validar na primeira execução real (ex.: no GitHub
Actions, que tem internet completa).
"""

import os

import requests

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource

API_URL_TEMPLATE = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"


class AdzunaSource(JobSource):
    name = "adzuna"

    def __init__(self, queries: list[dict], location: str = "", results_per_query: int = 20,
                 country: str = "br"):
        self.queries = queries
        self.location = location
        self.results_per_query = results_per_query
        self.country = country
        self.app_id = os.environ.get("ADZUNA_APP_ID")
        self.app_key = os.environ.get("ADZUNA_APP_KEY")

    def fetch_jobs(self) -> list[JobPosting]:
        if not self.app_id or not self.app_key:
            print("[adzuna] ADZUNA_APP_ID/ADZUNA_APP_KEY não configurados, pulando.")
            return []

        jobs: list[JobPosting] = []
        for query in self.queries:
            what = query.get("what", "")
            where = query.get("where", self.location)
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": what,
                "where": where,
                "results_per_page": self.results_per_query,
                "content-type": "application/json",
            }
            url = API_URL_TEMPLATE.format(country=self.country)
            try:
                resp = requests.get(url, params=params, timeout=15)
                resp.raise_for_status()
                payload = resp.json()
            except (requests.RequestException, ValueError) as exc:
                print(f"[adzuna] falha na busca '{what}': {exc}")
                continue

            for item in payload.get("results", []):
                jobs.append(JobPosting(
                    title=item.get("title", ""),
                    company=(item.get("company") or {}).get("display_name", ""),
                    url=item.get("redirect_url", ""),
                    source=self.name,
                    description=item.get("description", ""),
                    location=(item.get("location") or {}).get("display_name", ""),
                ))
        return jobs
