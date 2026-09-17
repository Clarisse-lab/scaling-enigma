"""Fonte de vagas: Upwork (trabalho freelance/contrato).

A API completa do Upwork (Upwork API v2/GraphQL) exige OAuth2 por
usuário e aprovação de app no portal de desenvolvedores — não dá pra
automatizar com uma simples chave como Adzuna/Jooble. Em vez disso, esta
fonte usa o feed RSS público de busca por palavra-chave, que é um
mecanismo oficial de sindicação (não scraping) e não exige login:

    https://www.upwork.com/ab/feed/jobs/rss?q=<query>&sort=recency

Não há confirmação de que esse feed segue ativo — o Upwork já restringiu
acesso público a dados de vagas no passado. Não foi possível testar ao
vivo a partir deste ambiente de desenvolvimento (sem acesso à internet
aberta); validar na primeira execução real (ex.: GitHub Actions). Se o
feed estiver fora do ar, esta fonte só vai logar um aviso e retornar
lista vazia, sem quebrar o resto da varredura.

Como o Upwork é freelance/contrato (não CLT/PJ tradicional), essas vagas
entram no mesmo ranking das demais — filtre/ignore manualmente se não
for o que você procura numa busca específica.
"""

import xml.etree.ElementTree as ET

import requests

from jobhunter.models import JobPosting
from jobhunter.sources.base import JobSource

FEED_URL = "https://www.upwork.com/ab/feed/jobs/rss"


class UpworkSource(JobSource):
    name = "upwork"

    def __init__(self, queries: list[dict], results_per_query: int = 20):
        self.queries = queries
        self.results_per_query = results_per_query

    def fetch_jobs(self) -> list[JobPosting]:
        jobs: list[JobPosting] = []
        for query in self.queries:
            what = query.get("what", "")
            if not what:
                continue
            try:
                resp = requests.get(
                    FEED_URL,
                    params={"q": what, "sort": "recency"},
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
            except (requests.RequestException, ET.ParseError) as exc:
                print(f"[upwork] falha na busca '{what}': {exc}")
                continue

            items = root.findall("./channel/item")[: self.results_per_query]
            for item in items:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                description = (item.findtext("description") or "").strip()
                jobs.append(JobPosting(
                    title=title,
                    company="",
                    url=link,
                    source=self.name,
                    description=description,
                ))
        return jobs
