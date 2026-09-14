from abc import ABC, abstractmethod

from jobhunter.models import JobPosting


class JobSource(ABC):
    """Interface comum para qualquer fonte de vagas."""

    name: str

    @abstractmethod
    def fetch_jobs(self, companies: list[str]) -> list[JobPosting]:
        """Retorna as vagas abertas para a lista de empresas informada."""
        raise NotImplementedError
