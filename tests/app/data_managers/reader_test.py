import os
from pathlib import Path

import pandas as pd
import pytest
from pytest import FixtureRequest

from app.constants import DataColumns
from app.data_managers.reader import LSEDataReader

MOCK_INPUT_DIR = Path("tests", "tmp")
MOCK_FILE_PATH = MOCK_INPUT_DIR / "lse_input.csv"

EXTRA_COLUMN_NAME = "extra_col"

stock_code_variation = DataColumns.STOCK_CODE.replace("_", " ").upper()
company_name_variation = DataColumns.COMPANY_NAME.replace("_", " ").capitalize()

stock_code_invalid_variation = DataColumns.STOCK_CODE.replace("_", "-")


@pytest.fixture(
    params=[
        # data with columns with spaces and mixed case
        pd.DataFrame(
            [
                {
                    stock_code_variation: "ABC",
                    company_name_variation: "Alpha Beta Corp",
                    DataColumns.TIMESTAMP: "",
                    DataColumns.VALUE: "",
                },
                {
                    stock_code_variation: "FBT",
                    company_name_variation: "Flobotics",
                    DataColumns.TIMESTAMP: "",
                    DataColumns.VALUE: "",
                },
            ]
        ),
        # valid data with correct column names
        pd.DataFrame(
            [
                {
                    DataColumns.STOCK_CODE: "ABC",
                    DataColumns.COMPANY_NAME: "Alpha Beta Corp",
                    DataColumns.TIMESTAMP: "",
                    DataColumns.VALUE: "",
                },
                {
                    DataColumns.STOCK_CODE: "FBT",
                    DataColumns.COMPANY_NAME: "Flobotics",
                    DataColumns.TIMESTAMP: "",
                    DataColumns.VALUE: "",
                },
            ]
        ),
        # only relevant columns: also allowed
        pd.DataFrame(
            [
                {
                    DataColumns.STOCK_CODE: "ABC",
                    DataColumns.COMPANY_NAME: "Alpha Beta Corp",
                },
                {
                    DataColumns.STOCK_CODE: "FBT",
                    DataColumns.COMPANY_NAME: "Flobotics",
                },
            ]
        ),
        # Extra unexpected column and random order of columns
        pd.DataFrame(
            [
                {
                    EXTRA_COLUMN_NAME: "ignored",
                    DataColumns.TIMESTAMP: "",
                    stock_code_variation: "ABC",
                    DataColumns.VALUE: "",
                    DataColumns.COMPANY_NAME: "Alpha Beta Corp",
                },
                {
                    EXTRA_COLUMN_NAME: "ignored",
                    DataColumns.TIMESTAMP: "123",
                    stock_code_variation: "FBT",
                    DataColumns.VALUE: "",
                    DataColumns.COMPANY_NAME: "Flobotics",
                },
            ]
        ),
        # Extra unexpected column, random order of columns and names variation
        pd.DataFrame(
            [
                {
                    EXTRA_COLUMN_NAME: "ignored",
                    DataColumns.TIMESTAMP: "",
                    stock_code_variation: "ABC",
                    DataColumns.VALUE: "",
                    DataColumns.COMPANY_NAME: "Alpha Beta Corp",
                },
                {
                    EXTRA_COLUMN_NAME: "ignored",
                    DataColumns.TIMESTAMP: "",
                    stock_code_variation: "FBT",
                    DataColumns.VALUE: "123",
                    DataColumns.COMPANY_NAME: "Flobotics",
                },
            ]
        ),
    ]
)
def valid_csv_file(request: FixtureRequest):
    """
    Fixture that writes a valid parametrized DataFrame to a CSV file.
    This file should be read correctly by the LSEDataReader.
    """

    os.makedirs(MOCK_INPUT_DIR, exist_ok=True)

    if MOCK_FILE_PATH.exists():
        MOCK_FILE_PATH.unlink()

    data: pd.DataFrame = request.param
    data.to_csv(MOCK_FILE_PATH, index=False)

    yield MOCK_FILE_PATH

    if MOCK_FILE_PATH.exists():
        MOCK_FILE_PATH.unlink()


@pytest.fixture(
    params=[
        # column names joined by any character different than underscore or space
        pd.DataFrame(
            [
                {
                    stock_code_invalid_variation: "ABC",
                    DataColumns.COMPANY_NAME: "Alpha Beta Corp",
                    DataColumns.TIMESTAMP: "",
                    DataColumns.VALUE: "",
                }
            ]
        ),
        # missing relevant column: stock_code
        pd.DataFrame(
            [
                {
                    DataColumns.STOCK_CODE: "ABC",
                    DataColumns.TIMESTAMP: "",
                    DataColumns.VALUE: "",
                }
            ]
        ),
    ]
)
def invalid_csv_file(request: FixtureRequest):
    """
    Fixture that writes an invalid parametrized DataFrame to a CSV file.
    This file should NOT be read correctly by the LSEDataReader
    and is intended to trigger errors.
    """

    os.makedirs(MOCK_INPUT_DIR, exist_ok=True)

    if MOCK_FILE_PATH.exists():
        MOCK_FILE_PATH.unlink()

    data: pd.DataFrame = request.param
    data.to_csv(MOCK_FILE_PATH, index=False)

    yield MOCK_FILE_PATH

    if MOCK_FILE_PATH.exists():
        MOCK_FILE_PATH.unlink()


class TestLSEDataReader:
    """Test suite for the LSEDataReader class."""

    def test_reads_data_correctly(self, valid_csv_file: str) -> None:
        """Test that data is read correctly from a valid CSV file."""

        reader = LSEDataReader()
        df = reader.read(valid_csv_file)

        assert not df.empty
        assert list(df.columns) == [
            DataColumns.COMPANY_NAME,
            DataColumns.STOCK_CODE,
        ]

        assert df.iloc[0][DataColumns.STOCK_CODE] == "ABC"
        assert df.iloc[0][DataColumns.COMPANY_NAME] == "Alpha Beta Corp"

        assert df.iloc[1][DataColumns.STOCK_CODE] == "FBT"
        assert df.iloc[1][DataColumns.COMPANY_NAME] == "Flobotics"

    def test_raises_error_for_nonexistent_file(self) -> None:
        """Test that FileNotFoundError is raised for a nonexistent file."""

        reader = LSEDataReader()

        with pytest.raises(FileNotFoundError):
            reader.read("nonexistent_file.csv")

    def test_raises_error_for_invalid_file(self, invalid_csv_file: str) -> None:
        """
        Test that KeyError is raised for an invalid CSV file,
        specifically when required columns are missing or misnamed.
        """

        reader = LSEDataReader()

        with pytest.raises(KeyError):
            reader.read(invalid_csv_file)
