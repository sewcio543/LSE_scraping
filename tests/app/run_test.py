from typing import Any

import numpy as np
import pandas as pd
import pytest
from pytest import MonkeyPatch

import app.exceptions as exc
import app.run as cli
from app.constants import DataColumns
from app.models.pydantic_models import StockRequest, StockResponse

STOCK_REQUEST: dict[str, Any] = {
    DataColumns.COMPANY_NAME: "Xylion Devices",
    DataColumns.STOCK_CODE: "XD",
}
STOCK_PARAMS = STOCK_REQUEST | {
    DataColumns.TIMESTAMP: "14.09.25 13:03:33 BST",
    DataColumns.VALUE: 160.35,
}
STOCK_FAILED_RESPONSE = STOCK_REQUEST | {
    DataColumns.TIMESTAMP: np.nan,
    DataColumns.VALUE: np.nan,
}


@pytest.fixture
def mock_data() -> pd.DataFrame:
    """Fixture providing a mock DataFrame for testing."""

    return pd.DataFrame([STOCK_REQUEST, STOCK_REQUEST])


class FakeDriver:
    """Fake Selenium driver for testing, always returns the same stock data."""

    def scrape(self, request: StockRequest) -> StockResponse:
        return StockResponse(**STOCK_PARAMS)

    def quit(self):
        pass


class FakeFailingDriver(FakeDriver):
    """Fake Selenium driver for testing, always raises ScrapingError."""

    def scrape(self, request: StockRequest) -> StockResponse:
        raise exc.ScrapingError("Failed to scrape")


class FakeMixedDriver:
    """
    Fake Selenium driver for testing:
    - first call to scrape -> returns success
    - second call -> raises ScrapingError
    """

    def __init__(self):
        self.calls = 0

    def scrape(self, request: StockRequest) -> StockResponse:
        if self.calls == 0:
            self.calls += 1
            return StockResponse(**STOCK_PARAMS)
        else:
            raise exc.ScrapingError("Failed to scrape")

    def quit(self):
        pass


@pytest.mark.integration
class TestCLIIntegration:
    """Tests for CLI main function."""

    @pytest.mark.parametrize(
        "driver_class, expected",
        [
            (FakeDriver, [STOCK_PARAMS, STOCK_PARAMS]),
            (FakeFailingDriver, [STOCK_FAILED_RESPONSE, STOCK_FAILED_RESPONSE]),
            (FakeMixedDriver, [STOCK_PARAMS, STOCK_FAILED_RESPONSE]),
        ],
    )
    def test_main_integration(
        self,
        tmp_path,
        monkeypatch: MonkeyPatch,
        mock_data: pd.DataFrame,
        driver_class: type[FakeDriver],
        expected: list[StockResponse],
    ):
        """
        Integration test for CLI main: mocks Selenium driver, checks output CSV.
        Checks for different driver behaviors (all success, all fail, mixed).
        """
        monkeypatch.setattr(cli, "get_driver", lambda headless=True: driver_class())

        input_path = tmp_path / "input.csv"
        output_path = tmp_path / "output.csv"

        mock_data.to_csv(input_path, index=False)

        cli.main(input_path=input_path, output_path=output_path)

        result = pd.read_csv(output_path)

        expected_df = pd.DataFrame(expected)
        pd.testing.assert_frame_equal(result, expected_df)
