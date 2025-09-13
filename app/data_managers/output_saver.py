"""
Module with classes for saving output data to various formats.
Contains IDataSaver interface and implementations for specific formats.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

import app.constants as consts
from app.logging import logger

# TODO: this may need some restructuring


class IDataSaver(ABC):
    """
    Interface for data savers. Defines a method to save data to a specified folder.
    """

    @abstractmethod
    def save(self, data: pd.DataFrame, output_folder: Path) -> None:
        """
        Saves the provided DataFrame to the specified output folder.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing the data to be saved.
        output_folder : Path
            Path to the folder where the output file will be saved.
        """
        raise NotImplementedError


class CSVSaver(IDataSaver):
    """
    Implementation of IDataSaver that saves data as a CSV file.
    Optionally includes a timestamp in the filename.
    """

    def __init__(
        self,
        include_timestamp: bool = True,
        file_name: str = consts.DEFAULT_OUTPUT_FILE_NAME,
    ) -> None:
        """
        Initializes the CSVSaver object.

        Parameters
        ----------
        include_timestamp : bool, optional
            Whether to include a timestamp in the filename, by default True.
        file_name : str, optional
            Base name for the output file, if not provided, uses default from constants.
        """
        self.include_timestamp = include_timestamp
        self.file_name = file_name

    def save(self, data: pd.DataFrame, output_folder: Path) -> None:
        self._ensure_folder_exists(output_folder)
        path = self._get_file_path(output_folder)

        data.to_csv(path, index=False)

        logger.info(f"Output saved to {path}")

    def _ensure_folder_exists(self, folder: Path) -> None:
        """Ensure the output folder exists, creating it if necessary."""
        folder.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, folder: Path) -> Path:
        """Construct the full file path for the output CSV file."""
        timestamp = datetime.now().strftime(consts.TIMESTAMP_FORMAT)
        name = (
            self.file_name
            if not self.include_timestamp
            else f"{self.file_name}_{timestamp}"
        )
        return folder / f"{name}.csv"
