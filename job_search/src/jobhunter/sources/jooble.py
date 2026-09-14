"""Fonte de vagas: Jooble — agregador com API pública de busca por
palavra-chave/localização (não precisa saber a empresa antes).

Requer chave gratuita em https://jooble.org/api/about, passada via
variável de ambiente: JOOBLE_API_KEY

Endpoint documentado: POST https://jooble.org/api/{api_key}
Body JSON: {"keywords": "...", "location": "..."}

Não foi possível testar ao vivo a partir deste ambiente de desenvolvimento
(sem acesso à internet aberta) — validar na primeira execução real (ex.:
no GitHub Actions, que tem internet completa).
"""

import os

import requests

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource

API_URL_TEMPLATE = "https://jooble.org/api/{api_key}"


class JoobleSource(JobSource):
    name = "jooble"

    def __init__(self, queries: list[dict], location: str = "", results_per_query: int = 20):
        self.queries = queries
        self.location = location
        self.results_per_query = results_per_query
        self.api_key = os.environ.get("JOOBLE_API_KEY")

    def fetch_jobs(self) -> list[JobPosting]:
        if not self.api_key:
            print("[jooble] JOOBLE_API_KEY não configurada, pulando.")
            return []

        jobs: list[JobPosting] = []
        url = API_URL_TEMPLATE.format(api_key=self.api_key)
        for query in self.queries:
            keywords = query.get("what", "")
            location = query.get("where", self.location)
            body = {"keywords": keywords, "location": location}
            try:
                resp = requests.post(url, json=body, timeout=15)
                resp.raise_for_status()
                payload = resp.json()
            except (requests.RequestException, ValueError) as exc:
                print(f"[jooble] falha na busca '{keywords}': {exc}")
                continue

            for item in payload.get("jobs", [])[:self.results_per_query]:
                jobs.append(JobPosting(
                    title=item.get("title", ""),
                    company=item.get("company", ""),
                    url=item.get("link", ""),
                    source=self.name,
                    description=item.get("snippet", ""),
                    location=item.get("location", ""),
                ))
        return jobs
