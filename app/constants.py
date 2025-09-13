from pathlib import Path

DATA_FOLDER = Path("data")

OUTPUT_FILE_NAME = "lse_stocks"

# scraping related constants
PRICE_TAG_CLASS = "price-tag"
STOCK_SCOPE_ID = "ticker"
TIMESTAMP_ANCESTOR_CLASS = "delay"
TIMESTAMP_TAG_TYPE = "span"


class LSEWebsite:
    BASE_URL = "https://www.londonstockexchange.com"
    STOCK_ENDPOINT = f"stock"
    PRICE_EXPLORER_URL = f"{BASE_URL}/live-markets/market-data-dashboard/price-explorer"


class DataColumns:
    COMPANY_NAME = "company_name"
    STOCK_CODE = "stock_code"
    TIMESTAMP = "timestamp"
    VALUE = "value"

    USE_COLUMNS = [COMPANY_NAME, STOCK_CODE]
