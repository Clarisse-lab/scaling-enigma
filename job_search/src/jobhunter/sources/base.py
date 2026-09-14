from abc import ABC, abstractmethod

from jobhunter.models import JobPosting


class JobSource(ABC):
    """Interface comum para qualquer fonte de vagas.

    Cada fonte recebe sua própria configuração (empresas, queries, chaves de
    API) no construtor e sabe buscar suas vagas sozinha.
    """

    name: str

    @abstractmethod
    def fetch_jobs(self) -> list[JobPosting]:
        """Retorna as vagas encontradas por esta fonte."""
        raise NotImplementedError
