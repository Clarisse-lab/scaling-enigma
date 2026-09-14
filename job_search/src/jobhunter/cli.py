"""Ponto de entrada: busca vagas em todas as fontes configuradas, pontua
e imprime o ranking.

Uso:
    cd job_search && python -m jobhunter.cli
"""

from pathlib import Path

import yaml

from jobhunter.matcher import load_keywords, rank_jobs
from jobhunter.sources.abler import AblerSource
from jobhunter.sources.bairesdev import BairesDevSource
from jobhunter.sources.gupy import GupySource
from jobhunter.sources.manual import ManualSource
from jobhunter.sources.solides import SolidesSource

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

SOURCES = {
    "gupy": GupySource(),
    "solides": SolidesSource(),
    "abler": AblerSource(),
    "bairesdev": BairesDevSource(),
}


def load_platforms(path: Path = CONFIG_DIR / "platforms.yaml") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def main() -> None:
    platforms = load_platforms()
    jobs = []

    for platform in platforms:
        if platform["mode"] != "api":
            continue
        source = SOURCES.get(platform["name"])
        if not source:
            continue
        companies = platform.get("companies") or []
        if not companies:
            print(f"[{platform['name']}] nenhuma empresa configurada em platforms.yaml, pulando.")
            continue
        jobs.extend(source.fetch_jobs(companies))

    jobs.extend(ManualSource().fetch_jobs())

    keywords = load_keywords()
    ranked = rank_jobs(jobs, keywords)

    if not ranked:
        print("Nenhuma vaga encontrada. Preencha as empresas-alvo em "
              "job_search/config/platforms.yaml e/ou vagas manuais em "
              "job_search/config/manual_jobs.yaml.")
        return

    print(f"{len(ranked)} vaga(s) encontrada(s), ranqueadas por relevância:\n")
    for job in ranked:
        print(f"[{job.score:>4.1f}] {job.title} — {job.company} ({job.source})")
        if job.matched_terms:
            print(f"        termos: {', '.join(job.matched_terms)}")
        print(f"        {job.url}")


if __name__ == "__main__":
    main()
