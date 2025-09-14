from unittest.mock import PropertyMock

import pytest
from pytest import MonkeyPatch

import app.constants as const
import app.exceptions as exc
from app.constants import LSEWebsite
from app.models.pydantic_models import StockRequest, StockResponse
from app.scraping.selenium_utils import LSEDriver, get_driver
from tests.app.scraping.conftest import get_driver_options, insert

mock_request = StockRequest(stock_code="XD", company_name="Xylion Devices")


def mock_raise():
    """Mock function that raises an exception just to test error handling."""
    raise Exception


timestamp = "14.09.25 13:03:33 BST"
price = 160.35
price_tag = f'<span class="{const.PRICE_TAG_CLASS}"> {price} </span>'

HTML_TEMPLATE = """
<div id="{ticker_id}">
    {price_tag}
    <div class="ticker-item delay">
        <div>
        As at
        <span>{timestamp}</span>
        - All data delayed at least 15 minutes
        </div>
    </div>
</div>
"""

DEFAULT_TEXT = HTML_TEMPLATE.format(
    ticker_id=const.STOCK_SCOPE_ID,
    price_tag=price_tag,
    timestamp=timestamp,
)


@pytest.fixture(scope="session")
def driver():
    """Fixture providing LSEDriver instance test session."""
    options = get_driver_options()
    driver = LSEDriver(options=options)

    yield driver

    driver.quit()


@pytest.mark.selenium
class TestLSEDriver:
    """Tests suite for LSEDriver class."""

    def test_scrapes_response_correctly(
        self, monkeypatch: MonkeyPatch, driver: LSEDriver
    ):
        """
        Tests that scrape method returns correct StockResponse object
        if process was finished without errors and elements were found correctly.
        """
        monkeypatch.setattr(LSEDriver, "get", lambda self, url: None)

        text = DEFAULT_TEXT
        insert(text, driver)
        result = driver.scrape(mock_request)

        expected = StockResponse(
            company_name="Xylion Devices",
            stock_code="XD",
            timestamp="14.09.25 13:03:33 BST",
            value=160.35,
        )
        assert result == expected

    def test_raises_error_when_redirected_to_price_explorer(
        self, monkeypatch: MonkeyPatch, driver: LSEDriver
    ):
        """
        Tests that PageLoadError is raised when driver is redirected to LSE
        price explorer page instead of stock details page. `current_url` is mocked
        to simulate redirection.
        """
        monkeypatch.setattr(
            LSEDriver,
            "current_url",
            PropertyMock(return_value=LSEWebsite.PRICE_EXPLORER_URL),
        )
        monkeypatch.setattr(LSEDriver, "get", lambda self, url: None)

        text = DEFAULT_TEXT
        insert(text, driver)

        with pytest.raises(exc.PageLoadError):
            driver.scrape(mock_request)

    def test_raises_error_when_base_element_not_found_on_page(
        self, monkeypatch: MonkeyPatch, driver: LSEDriver
    ):
        """
        Tests that PageLoadError is raised when base element is not found on page.
        Element of id `ticker` is missing in mocked HTML.
        """
        monkeypatch.setattr(LSEDriver, "get", lambda self, url: None)

        text = HTML_TEMPLATE.format(
            ticker_id="not-ticker-id",
            price_tag=price_tag,
            timestamp=timestamp,
        )

        insert(text, driver)

        with pytest.raises(exc.PageLoadError):
            driver.scrape(mock_request)

    def test_raises_error_when_connection_failed(
        self, monkeypatch: MonkeyPatch, driver: LSEDriver
    ):
        """
        Tests if PageLoadError is raised when connection to the page fails.
        `get` method is mocked to raise an exception simulating connection error.
        """
        monkeypatch.setattr(LSEDriver, "get", lambda self, url: mock_raise())

        text = DEFAULT_TEXT
        insert(text, driver)

        with pytest.raises(exc.PageLoadError):
            driver.scrape(mock_request)

    def test_raises_error_when_scraping_failed(
        self, monkeypatch: MonkeyPatch, driver: LSEDriver
    ):
        """
        Tests if ElementNotFoundError is raised when scraping with soupsavvy fails.
        HTML was intentionally malformed - price tag is empty, so model fails
        to find required elements.
        """
        monkeypatch.setattr(LSEDriver, "get", lambda self, url: None)

        text = HTML_TEMPLATE.format(
            ticker_id=const.STOCK_SCOPE_ID,
            price_tag="",
            timestamp=timestamp,
        )
        insert(text, driver)

        with pytest.raises(exc.ElementNotFoundError):
            driver.scrape(mock_request)

    def test_handles_price_with_commas(
        self, monkeypatch: MonkeyPatch, driver: LSEDriver
    ):
        """
        Tests that price with commas (in thousands) is handled correctly
        and converted to float properly. All this is handled by soupsavvy model.
        """
        monkeypatch.setattr(LSEDriver, "get", lambda self, url: None)

        text = HTML_TEMPLATE.format(
            ticker_id=const.STOCK_SCOPE_ID,
            price_tag=f'<span class="{const.PRICE_TAG_CLASS}"> 1,234.50 </span>',
            timestamp=timestamp,
        )
        insert(text, driver)

        result = driver.scrape(mock_request)

        expected = StockResponse(
            company_name="Xylion Devices",
            stock_code="XD",
            timestamp="14.09.25 13:03:33 BST",
            value=1234.50,
        )
        assert result == expected


@pytest.mark.selenium
class TestGetDriver:
    """Tests suite for get_driver function."""

    def test_gets_driver_instance(self):
        """Tests that get_driver returns LSEDriver instance."""
        driver = get_driver()
        assert isinstance(driver, LSEDriver)
