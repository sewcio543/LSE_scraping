"""
Utilities for setting up and using Selenium WebDriver
to scrape stock data from the LSE website.
"""

from sys import platform
from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from soupsavvy.exceptions import BaseModelException
from soupsavvy.implementation.selenium import SeleniumElement

import app.constants as const
import app.exceptions as exc
from app.data_managers.parsers import parse_url
from app.logging import logger
from app.models.pydantic_models import StockRequest, StockResponse
from app.models.soupsavvy_models import StockScraperModel

# driver options
# TODO: extract maybe
OPTIONS_ARGS = ["--disable-popup-blocking", "--disable-extensions", "--headless"]

EXPERIMENTAL_OPTS = {
    "excludeSwitches": ["enable-logging", "disable-popup-blocking"],
}

if platform == "linux":  # pragma: no cover
    OPTIONS_ARGS += [
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--user-data-dir=driver_logs",
    ]


class LSEDriver(Chrome):
    """
    Custom Selenium WebDriver for scraping LSE stock data.
    Inludes extra functionality specific to LSE website
    for navigating and extracting stock information.
    """

    # TODO: exception handling to quit driver
    def scrape(self, requests: list[StockRequest]) -> list[StockResponse]:
        """
        Scrapes stock data for the given list of StockRequest objects.

        Parameters
        ----------
        requests : list[StockRequest]
            List of StockRequest objects containing stock_code and company_name.

        Returns
        -------
        list[StockResponse]
            List of StockResponse objects with scraped data.

        Raises
        -------
        exc.PageLoadError
            If a stock page fails to load properly or structure has changed.
        exc.ScrapingError
            If required elements cannot be found on the page.
        """
        responses = []

        for request in requests:
            url = parse_url(request)

            try:
                self._navigate_to_stock_page(url)
            except exc.PageLoadError as e:
                response = StockResponse(
                    company_name=request.company_name,
                    stock_code=request.stock_code,
                    timestamp=None,
                    value=None,
                )
                responses.append(response)
                logger.error(f"Error loading page for {url}: {e} - no data retrieved")
                continue

            element = self._get_element()

            try:
                scraped = StockScraperModel.find(element)
            except BaseModelException as e:
                raise exc.ScrapingError(f"Error scraping data for {url}: {e}") from e

            response = scraped.migrate(
                StockResponse,
                company_name=request.company_name,
                stock_code=request.stock_code,
            )
            responses.append(response)

        self.quit()
        return responses

    def _navigate_to_stock_page(self, url: str) -> Self:
        """
        Navigates to the stock details page for the given URL.
        Checks if the page loaded correctly and expected elements are present.
        """
        self.get(url)

        if not self._is_valid_stock_page():
            raise exc.PageLoadError(
                f"Stock details page not found on LSE website for url: {url}"
            )

        self._wait_for_page_load()
        return self

    def _get_element(self) -> SeleniumElement:
        """
        Retrieves the root HTML element of the current page
        and wraps it in soupsavvy SeleniumElement.
        """
        node = self.find_element(By.TAG_NAME, "html")
        return SeleniumElement(node)

    def _is_valid_stock_page(self) -> bool:
        """
        Checks if the current page is a valid stock details page (was not redirected).
        """
        return self.current_url != const.LSEWebsite.PRICE_EXPLORER_URL

    def _wait_for_page_load(self, timeout: int = 10) -> Self:
        """
        Waits until the main stock data element is present on the page.
        If not found within the timeout, raises PageLoadError.
        """
        try:
            WebDriverWait(self, timeout).until(
                EC.presence_of_element_located((By.ID, const.STOCK_SCOPE_ID))
            )
        except TimeoutException:
            raise exc.PageLoadError(
                "Required web elements not found within the timeout period, "
                "structure of the website may have changed for given stock."
            )
        return self


# TODO: clean up these options
def get_driver() -> LSEDriver:
    """
    Sets up and returns a configured LSEDriver instance.

    Returns
    -------
    LSEDriver - Configured Selenium WebDriver for LSE scraping.
    """
    opts = Options()

    for arg in OPTIONS_ARGS:
        opts.add_argument(arg)
    for key, value in EXPERIMENTAL_OPTS.items():
        opts.add_experimental_option(key, value)

    return LSEDriver(options=opts)
