"""
Module with classes for reading and processing data files.
Contains Reader interface and specific implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from app.constants import DataColumns
from app.types import PathType


class IDataReader(ABC):
    """
    Interface for data readers. Defines a method to read data from a given path.
    """

    @abstractmethod
    def read(self, path: PathType) -> pd.DataFrame:
        """
        Reads data from the specified path and returns it as a DataFrame.

        Parameters
        ----------
        path : PathType
            Path to the data file, either as a string or Path object.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the read data.
        """
        raise NotImplementedError("Subclasses must implement this method")


class LSEDataReader(IDataReader):
    """
    Implementation of IDataReader for London Stock Exchange data files
    in the format provided by client. Reads only relevant columns and renames them
    to processing friendly names.
    """

    def read(self, path: PathType) -> pd.DataFrame:
        data = pd.read_csv(path)
        columns = [col.replace(" ", "_").lower() for col in data.columns]
        data.columns = columns
        data = data[DataColumns.USE_COLUMNS]
        return data
