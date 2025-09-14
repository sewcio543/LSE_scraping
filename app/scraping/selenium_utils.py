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
from app.models.pydantic_models import StockRequest, StockResponse
from app.models.soupsavvy_models import StockScraperModel

page_loaded_condition = EC.presence_of_element_located((By.ID, const.STOCK_SCOPE_ID))


class LSEDriver(Chrome):
    """
    Custom Selenium WebDriver for scraping LSE stock data.
    Inludes extra functionality specific to LSE website
    for navigating and extracting stock information.
    """

    def scrape(self, request: StockRequest) -> StockResponse:
        """
        Scrapes stock data for the given StockRequest object.

        Parameters
        ----------
        request : StockRequest
            StockRequest object containing stock_code and company_name.

        Returns
        -------
        StockResponse
            StockResponse object with scraped data.

        Notes
        -----
        Method does not handle driver lifecycle (opening/closing).
        Caller is responsible for managing the driver's lifecycle.

        Raises
        -------
        exc.PageLoadError
            If a stock page fails to load properly or structure has changed.
        exc.ScrapingError
            If required elements cannot be found on the page.
        """
        url = parse_url(request)
        self._navigate_to_stock_page(url)
        element = self._get_element()

        try:
            scraped = StockScraperModel.find(element)
        except BaseModelException as e:
            raise exc.ElementNotFoundError(f"Error scraping data for {url}: {e}") from e

        response = scraped.migrate(
            StockResponse,
            company_name=request.company_name,
            stock_code=request.stock_code,
        )
        return response

    def _navigate_to_stock_page(self, url: str) -> Self:
        """
        Navigates to the stock details page for the given URL.
        Checks if the page loaded correctly and expected elements are present.
        """
        try:
            self.get(url)
        except Exception as e:  # network error, timeout, Chrome crash
            raise exc.PageLoadError(f"Failed to load {url}: {e}") from e

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

    def _wait_for_page_load(self, timeout: int = const.DEFAULT_TIMEOUT) -> Self:
        """
        Waits until the main stock data element is present on the page.
        If not found within the timeout, raises PageLoadError.
        """
        try:
            WebDriverWait(self, timeout).until(page_loaded_condition)
        except TimeoutException:
            raise exc.PageLoadError(
                "Required web elements not found within the timeout period, "
                "structure of the website may have changed for given stock."
            )
        return self


def _build_chrome_options(headless: bool = True) -> Options:
    """Build and return Chrome Options configured for LSE scraping."""

    opts = Options()
    args = const.CHROME_DEFAULT_ARGS

    if headless:
        args.append("--headless")

    if platform == "linux":  # pragma: no cover
        args.extend(const.CHROME_LINUX_ARGS)

    for arg in args:
        opts.add_argument(arg)

    for key, value in const.CHROME_EXPERIMENTAL.items():
        opts.add_experimental_option(key, value)

    return opts


def get_driver(headless: bool = True) -> LSEDriver:
    """
    Sets up and returns a configured LSEDriver instance.

    Parameters
    ----------
    headless : bool, optional
        Whether to run the browser in headless mode, by default True.

    Returns
    -------
    LSEDriver - Configured Selenium WebDriver for LSE scraping.
    """
    opts = _build_chrome_options(headless=headless)
    return LSEDriver(options=opts)
