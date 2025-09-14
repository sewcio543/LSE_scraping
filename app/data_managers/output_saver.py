"""
Module with classes for saving output data to various formats.
Contains IDataSaver interface and implementations for specific formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from app.types import PathType


class IDataSaver(ABC):
    """
    Interface for data savers. Defines a method to save data to a specified folder.
    """

    def save(self, data: pd.DataFrame, path: PathType) -> None:
        """
        Saves the provided DataFrame to the specified output folder.
        Ensures the output directory exists before saving.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing the data to be saved.
        path : PathType
            Path to the file where the data will be saved.
        """
        path = Path(path)
        directory = path.parent

        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)

        self._save(data=data, path=path)

    @abstractmethod
    def _save(self, data: pd.DataFrame, path: Path) -> None:
        """
        Internal method to save the DataFrame to the specified path.
        Must be implemented by subclasses.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing the data to be saved.
        path : Path
            Path to the file where the data will be saved.
        """
        raise NotImplementedError("Subclasses must implement this method")


class CSVSaver(IDataSaver):
    """
    Implementation of IDataSaver that saves data as a CSV file.
    Optionally includes a timestamp in the filename.
    """

    def _save(self, data: pd.DataFrame, path: Path) -> None:
        data.to_csv(path, index=False)
