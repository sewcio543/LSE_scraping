import os
import shutil
from pathlib import Path

import pandas as pd
import pytest

import app.constants as consts
from app.data_managers.output_saver import CSVSaver

TMP_DIRECTORY = Path("tests", "mock_data", "tmp")


@pytest.fixture(scope="session")
def mock_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
    )


class TestCSVSaver:
    def test_save_dataframe_to_existing_directory(
        self, tmp_path: Path, mock_data: pd.DataFrame
    ):
        saver = CSVSaver()
        path = tmp_path / "test_output.csv"

        saver.save(data=mock_data, path=path)
        assert Path(path).exists()

        actual = pd.read_csv(path)
        pd.testing.assert_frame_equal(actual, mock_data)

    @pytest.mark.parametrize(
        "path",
        [
            Path("subdir1", "test_output.csv"),
            Path("subdir1", "subdir2", "test_output.csv"),
            str(Path("subdir1", "subdir2", "test_output.csv")),
        ],
    )
    def test_save_creates_non_existing_directories(
        self, tmp_path: Path, path: str | Path
    ):
        data = pd.DataFrame(
            [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        )
        saver = CSVSaver()
        full_path = tmp_path / path

        saver.save(data=data, path=full_path)
        assert full_path.exists()

        actual = pd.read_csv(full_path)
        pd.testing.assert_frame_equal(actual, data)
