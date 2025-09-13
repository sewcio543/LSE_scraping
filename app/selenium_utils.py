from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from soupsavvy.implementation.selenium import SeleniumElement

import app.constants as const
import app.exceptions as exc
from app.models.pydantic_models import StockRequest, StockResponse
from app.models.soupsavvy_models import StockScraperModel


def get_url(stock_info: StockRequest) -> str:
    url_parts = [
        const.LSEWebsite.BASE_URL,
        const.LSEWebsite.STOCK_ENDPOINT,
        stock_info.stock_code,
        stock_info.company_name.lower().replace(" ", "-"),
        "company-page",
    ]
    return "/".join(url_parts)


class LSEDriver(Chrome):

    def scrape(self, requests: list[StockRequest]) -> list[StockResponse]:
        responses = []

        for request in requests:
            url = get_url(request)

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
                continue

            element = self.get_element()
            scraped = StockScraperModel.find(element)
            response = scraped.migrate(
                StockResponse,
                company_name=request.company_name,
                stock_code=request.stock_code,
            )
            responses.append(response)

        self.quit()
        return responses

    def _navigate_to_stock_page(self, url: str) -> Self:
        self.get(url)

        if not self._is_valid_stock_page():
            # TODO: errors
            raise exc.PageLoadError(f"Invalid stock code in URL: {url}")

        self._wait_for_page_load()
        return self

    def get_element(self) -> SeleniumElement:
        node = self.find_element(By.TAG_NAME, "html")
        return SeleniumElement(node)

    def _is_valid_stock_page(self) -> bool:
        return self.current_url != const.LSEWebsite.PRICE_EXPLORER_URL

    def _wait_for_page_load(self, timeout: int = 10) -> Self:
        try:
            WebDriverWait(self, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, const.PRICE_TAG_CLASS))
            )
        except TimeoutException:
            raise exc.PageLoadError(
                "Required elements did not load within the given time."
            )
        return self


def get_driver() -> LSEDriver:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_experimental_option(
        "excludeSwitches", ["enable-logging", "disable-popup-blocking"]
    )
    return LSEDriver(options=opts)
