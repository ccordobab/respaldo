from abc import ABC, abstractmethod
from pathlib import Path

class CloudProvider(ABC):
    @abstractmethod
    def upload_file(self, file_path: Path, remote_folder: str = None) -> str:
        """Sube archivo y devuelve URL o ID del archivo"""
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """Realiza autenticación OAuth"""
        pass