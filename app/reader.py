from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from app.constants import DataColumns

PathType = str | Path


class DataReader(ABC):
    @abstractmethod
    def read(self, path: PathType) -> pd.DataFrame:
        raise NotImplementedError


class LSEDataReader(DataReader):
    def read(self, path: PathType) -> pd.DataFrame:
        new_cols = [
            DataColumns.COMPANY_NAME,
            DataColumns.STOCK_CODE,
            DataColumns.TIMESTAMP,
            DataColumns.VALUE,
        ]
        data = pd.read_csv(
            path,
            usecols=DataColumns.USE_COLUMNS,
            names=new_cols,
            header=0,
        )
        return data
