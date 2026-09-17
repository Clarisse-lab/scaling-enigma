"""Ponto de entrada: busca vagas em todas as fontes configuradas, pontua,
imprime o ranking e (opcionalmente) grava um relatório em Markdown.

Uso:
    cd job_search && python -m jobhunter.cli
    cd job_search && python -m jobhunter.cli --report results/2026-09-14.md
"""

import argparse
from pathlib import Path

import yaml

from jobhunter.filters import filter_remote_only
from jobhunter.matcher import load_keywords, rank_jobs
from jobhunter.models import JobPosting
from jobhunter.sources.abler import AblerSource
from jobhunter.sources.adzuna import AdzunaSource
from jobhunter.sources.bairesdev import BairesDevSource
from jobhunter.sources.gupy import GupySource
from jobhunter.sources.jooble import JoobleSource
from jobhunter.sources.manual import ManualSource
from jobhunter.sources.solides import SolidesSource
from jobhunter.sources.upwork import UpworkSource

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

COMPANY_SOURCES = {
    "gupy": GupySource,
    "solides": SolidesSource,
    "abler": AblerSource,
    "bairesdev": BairesDevSource,
}


def load_yaml(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_sources(search_cfg: dict) -> list:
    """Monta a lista de fontes a consultar: agregadores por área
    (Adzuna/Jooble) + fontes por empresa opcionais + entradas manuais."""
    sources = []

    queries = search_cfg.get("queries", [])
    location = search_cfg.get("location", "")
    results_per_query = search_cfg.get("results_per_query", 20)

    if queries:
        sources.append(AdzunaSource(queries, location, results_per_query))
        sources.append(JoobleSource(queries, location, results_per_query))
        if search_cfg.get("include_upwork", True):
            sources.append(UpworkSource(queries, results_per_query))

    platforms = load_yaml(CONFIG_DIR / "platforms.yaml")
    for platform in platforms:
        if platform.get("mode") != "api":
            continue
        source_cls = COMPANY_SOURCES.get(platform["name"])
        companies = platform.get("companies") or []
        if source_cls and companies:
            sources.append(source_cls(companies))

    sources.append(ManualSource())
    return sources


def format_report(jobs: list[JobPosting]) -> str:
    lines = [f"# Vagas encontradas ({len(jobs)})", ""]
    if not jobs:
        lines.append("Nenhuma vaga encontrada nesta varredura.")
        return "\n".join(lines)

    for job in jobs:
        lines.append(f"## [{job.score:.1f}] {job.title} — {job.company}")
        lines.append(f"- Fonte: {job.source}")
        if job.location:
            lines.append(f"- Local: {job.location}")
        if job.matched_terms:
            lines.append(f"- Termos: {', '.join(job.matched_terms)}")
        lines.append(f"- Link: {job.url}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=None,
                         help="Caminho para gravar o relatório em Markdown")
    parser.add_argument("--top", type=int, default=30,
                         help="Máximo de vagas no relatório/saída")
    args = parser.parse_args()

    search_cfg = load_yaml(CONFIG_DIR / "search.yaml")

    jobs: list[JobPosting] = []
    for source in build_sources(search_cfg):
        found = source.fetch_jobs()
        jobs.extend(found)

    if search_cfg.get("remote_only", False):
        before = len(jobs)
        jobs = filter_remote_only(jobs)
        print(f"Filtro remoto: {before} vaga(s) encontradas, {len(jobs)} mencionam trabalho remoto.\n")

    keywords = load_keywords()
    ranked = rank_jobs(jobs, keywords)[: args.top]

    if not ranked:
        print("Nenhuma vaga encontrada. Verifique se ADZUNA_APP_ID/ADZUNA_APP_KEY "
              "e/ou JOOBLE_API_KEY estão configurados, ou adicione vagas manuais em "
              "job_search/config/manual_jobs.yaml.")
    else:
        print(f"{len(ranked)} vaga(s) encontrada(s), ranqueadas por relevância:\n")
        for job in ranked:
            print(f"[{job.score:>4.1f}] {job.title} — {job.company} ({job.source})")
            if job.matched_terms:
                print(f"        termos: {', '.join(job.matched_terms)}")
            print(f"        {job.url}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(format_report(ranked), encoding="utf-8")
        print(f"\nRelatório gravado em {args.report}")


if __name__ == "__main__":
    main()
