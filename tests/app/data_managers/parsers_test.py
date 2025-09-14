import pandas as pd
import pytest

import app.exceptions as exc
from app.constants import DataColumns, LSEWebsite
from app.data_managers.parsers import parse_requests, parse_url
from app.models.pydantic_models import StockRequest


@pytest.fixture
def data() -> pd.DataFrame:
    """Fixture providing sample DataFrame representing input data for testing."""

    return pd.DataFrame(
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
    )


class TestParseRequests:
    """Test suite for the parse_requests function."""

    def test_parses_dataframe_to_stock_requests_correctly(
        self, data: pd.DataFrame
    ) -> None:
        """Test that a valid DataFrame is correctly parsed into StockRequest objects."""

        requests = parse_requests(data)

        assert len(requests) == 2
        assert all(isinstance(req, StockRequest) for req in requests)

        assert requests[0].stock_code == "ABC"
        assert requests[0].company_name == "Alpha Beta Corp"

        assert requests[1].stock_code == "FBT"
        assert requests[1].company_name == "Flobotics"

    def test_raises_error_when_required_column_missing(
        self, data: pd.DataFrame
    ) -> None:
        """Test that missing required columns raise a DataValidationError."""

        invalid_data = data.drop(columns=[DataColumns.STOCK_CODE])

        with pytest.raises(exc.DataValidationError):
            parse_requests(invalid_data)

    def test_raises_error_when_extra_column(self, data: pd.DataFrame) -> None:
        """
        Test that extra columns raise a DataValidationError.
        It's not a default pydantic behavior, but model was set up this way
        to ensure integrity of input data.
        """

        invalid_data = data.assign(**{"pumpumpum": [1, 2]})

        with pytest.raises(exc.DataValidationError):
            parse_requests(invalid_data)


class TestParseUrl:
    """Test suite for the parse_url function."""

    def test_constructs_url_correctly(self) -> None:
        """
        Test that the URL is constructed correctly from StockRequest data.
        Stock code is unchanged, company name is lowercased
        and spaces are replaced with hyphens. Url parts are joined with slashes
        and need to be in specified order with suffix at the end.
        """

        stock_info = StockRequest(stock_code="ABC", company_name="Alpha Beta Corp")

        url = parse_url(stock_info)

        expected_url = (
            f"{LSEWebsite.BASE_URL}/{LSEWebsite.STOCK_ENDPOINT}/ABC/alpha-beta-corp"
        )
        assert url == expected_url
