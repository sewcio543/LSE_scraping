from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

import app.constants as consts
from app.logging import logger


class DataSaver(ABC):
    @abstractmethod
    def save(self, data: pd.DataFrame, output_folder: Path) -> None:
        raise NotImplementedError


class CSVSaver(DataSaver):
    def __init__(
        self,
        include_timestamp: bool = True,
        file_name: str = consts.OUTPUT_FILE_NAME,
    ) -> None:
        self.include_timestamp = include_timestamp
        self.file_name = file_name

    def save(self, data: pd.DataFrame, output_folder: Path) -> None:
        self._ensure_folder_exists(output_folder)
        path = self._get_file_path(output_folder)

        data.to_csv(path, index=False)

        logger.info(f"Output saved to {path}")

    def _ensure_folder_exists(self, folder: Path) -> None:
        folder.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, folder: Path) -> Path:
        timestamp = datetime.now().strftime(consts.TIMESTAMP_FORMAT)
        name = (
            self.file_name
            if not self.include_timestamp
            else f"{self.file_name}_{timestamp}"
        )
        return folder / f"{name}.csv"
