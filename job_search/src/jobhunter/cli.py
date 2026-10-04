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
from jobhunter.matcher import dedupe_jobs, load_keywords, rank_jobs
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

OUTRAS_GROUP = "outras"
OUTRAS_LABEL = "Outras fontes (manual / por empresa)"


def load_yaml(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def flatten_query_groups(query_groups: dict) -> tuple[list[dict], dict[str, str]]:
    """Achata {grupo: {label, queries}} numa lista única de queries, cada
    uma marcada com `group`, e devolve também grupo -> label pra exibição."""
    queries = []
    labels = {}
    for group_key, group_cfg in query_groups.items():
        labels[group_key] = group_cfg.get("label", group_key)
        for query in group_cfg.get("queries", []):
            queries.append({**query, "group": group_key})
    return queries, labels


def build_sources(search_cfg: dict, queries: list[dict]) -> list:
    """Monta a lista de fontes a consultar: agregadores por área
    (Adzuna/Jooble) + fontes por empresa opcionais + entradas manuais."""
    sources = []

    location = search_cfg.get("location", "")
    jooble_location = search_cfg.get("jooble_location", location)
    results_per_query = search_cfg.get("results_per_query", 20)

    if queries:
        sources.append(AdzunaSource(queries, location, results_per_query))
        sources.append(JoobleSource(queries, jooble_location, results_per_query))
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


def group_jobs(jobs: list[JobPosting]) -> dict[str, list[JobPosting]]:
    """Separa a lista já ranqueada (ordem preservada) por query_group,
    jogando vagas sem grupo (manual/por empresa) num grupo 'outras'."""
    buckets: dict[str, list[JobPosting]] = {}
    for job in jobs:
        key = job.query_group or OUTRAS_GROUP
        buckets.setdefault(key, []).append(job)
    return buckets


def format_report(buckets: dict[str, list[JobPosting]], labels: dict[str, str], top_per_group: int) -> str:
    total = sum(len(jobs) for jobs in buckets.values())
    lines = [f"# Vagas encontradas ({total})", ""]
    if total == 0:
        lines.append("Nenhuma vaga encontrada nesta varredura.")
        return "\n".join(lines)

    for group_key, jobs in buckets.items():
        label = labels.get(group_key, OUTRAS_LABEL)
        section = jobs[:top_per_group]
        lines.append(f"## Seção: {label} ({len(jobs)})")
        lines.append("")
        for job in section:
            lines.append(f"### [{job.score:.1f}] {job.title} — {job.company}")
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
    parser.add_argument("--top", type=int, default=None,
                         help="Máximo de vagas por grupo no relatório/saída "
                              "(sobrescreve top_per_group de search.yaml)")
    args = parser.parse_args()

    search_cfg = load_yaml(CONFIG_DIR / "search.yaml")
    queries, labels = flatten_query_groups(search_cfg.get("query_groups", {}))
    top_per_group = args.top or search_cfg.get("top_per_group", 15)

    jobs: list[JobPosting] = []
    for source in build_sources(search_cfg, queries):
        found = source.fetch_jobs()
        jobs.extend(found)

    before_dedupe = len(jobs)
    jobs = dedupe_jobs(jobs)
    if before_dedupe != len(jobs):
        print(f"Duplicatas removidas: {before_dedupe} -> {len(jobs)} vaga(s) únicas.\n")

    if search_cfg.get("remote_only", False):
        before = len(jobs)
        jobs = filter_remote_only(jobs)
        print(f"Filtro remoto: {before} vaga(s) encontradas, {len(jobs)} mencionam trabalho remoto.\n")

    keywords = load_keywords()
    ranked = rank_jobs(jobs, keywords)
    buckets = group_jobs(ranked)

    if not ranked:
        print("Nenhuma vaga encontrada. Verifique se ADZUNA_APP_ID/ADZUNA_APP_KEY "
              "e/ou JOOBLE_API_KEY estão configurados, ou adicione vagas manuais em "
              "job_search/config/manual_jobs.yaml.")
    else:
        for group_key, group_jobs_list in buckets.items():
            label = labels.get(group_key, OUTRAS_LABEL)
            section = group_jobs_list[:top_per_group]
            print(f"== {label} ({len(group_jobs_list)} vaga(s), mostrando {len(section)}) ==\n")
            for job in section:
                print(f"[{job.score:>4.1f}] {job.title} — {job.company} ({job.source})")
                if job.matched_terms:
                    print(f"        termos: {', '.join(job.matched_terms)}")
                print(f"        {job.url}")
            print()

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(format_report(buckets, labels, top_per_group), encoding="utf-8")
        print(f"Relatório gravado em {args.report}")


if __name__ == "__main__":
    main()
