"""Module containing constants used across the application."""

# saving related constants
DEFAULT_OUTPUT_FOLDER = "output"
DEFAULT_OUTPUT_FILE_NAME = "lse_stocks"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# scraping related constants
PRICE_TAG_CLASS = "price-tag"
STOCK_SCOPE_ID = "ticker"
TIMESTAMP_ANCESTOR_CLASS = "delay"
TIMESTAMP_TAG_TYPE = "span"


class LSEWebsite:
    """Constants for the London Stock Exchange website. Contains urls and endpoints."""

    BASE_URL = "https://www.londonstockexchange.com"
    STOCK_ENDPOINT = f"stock"
    # it's a page where LSE websites redirects when url for stock details is invalid
    PRICE_EXPLORER_URL = f"{BASE_URL}/live-markets/market-data-dashboard/price-explorer"
    URL_SUFFIX = "company-page"


class DataColumns:
    """Column names for the LSE stock data after transformations."""

    COMPANY_NAME = "company_name"
    STOCK_CODE = "stock_code"
    TIMESTAMP = "timestamp"
    VALUE = "value"

    USE_COLUMNS = [COMPANY_NAME, STOCK_CODE]
