"""Filtro heurístico de vagas remotas.

Nem Adzuna nem Jooble expõem um parâmetro oficial e confiável de "só
remoto" pro Brasil, então a abordagem é por palavra-chave: mantém só
vagas cujo título/descrição/local mencionem trabalho remoto. Isso pode
deixar passar falso positivo (empresa remota citada só no rodapé do
anúncio) ou negativo (vaga remota que não usa nenhum desses termos) —
ajuste REMOTE_KEYWORDS conforme observar os resultados reais.
"""

from jobhunter.models import JobPosting

# Frases que afirmam remoto sem ambiguidade — bastam por si só.
STRONG_REMOTE_KEYWORDS = [
    "home office",
    "trabalho remoto",
    "100% remoto",
    "totalmente remoto",
    "remote work",
    "anywhere",
]

# "remoto"/"remota" isoladas são ambíguas: aparecem tanto em "vaga remota"
# quanto em negações como "sem possibilidade remota". Só contam se não
# houver sinal de presencial/híbrido por perto.
WEAK_REMOTE_KEYWORDS = ["remoto", "remota", "remote"]
ONSITE_KEYWORDS = ["presencial", "híbrido", "hibrido"]


def is_remote(job: JobPosting) -> bool:
    text = f"{job.title}\n{job.description}\n{job.location}".lower()

    if any(keyword in text for keyword in STRONG_REMOTE_KEYWORDS):
        return True

    has_weak_signal = any(keyword in text for keyword in WEAK_REMOTE_KEYWORDS)
    has_onsite_signal = any(keyword in text for keyword in ONSITE_KEYWORDS)
    return has_weak_signal and not has_onsite_signal


def filter_remote_only(jobs: list[JobPosting]) -> list[JobPosting]:
    return [job for job in jobs if is_remote(job)]
