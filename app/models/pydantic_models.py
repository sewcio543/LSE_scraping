"""
Module defining Pydantic models representing scraping request and response structures.
Used for data validation and serialization.

Can be used for easy integration with API frameworks if needed.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class StockRequest(BaseModel):
    """
    Model representing a request for stock data.
    Initialized from single row of input DataFrame provided by client.
    Contains all necessary information to build url
    and perform scraping for a single stock.


    Parameters
    ----------
    company_name : str
        Name of the company whose stock data is to be scraped.
    stock_code : str
        Stock code (ticker symbol) of the company listed on LSE.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    company_name: str
    stock_code: str


class StockResponse(BaseModel):
    """
    Model representing the response after scraping stock data.
    Contains the original request data along with the scraped value and timestamp.

    Parameters
    ----------
    company_name : str
        Name of the company whose stock data was scraped.
    stock_code : str
        Stock code (ticker symbol) of the stock that was scraped.
    timestamp : str
        Timestamp indicated by LSE website when scraped stock value was last updated.
    value : float
        Scraped value of the stock.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    company_name: str
    stock_code: str
    timestamp: str
    value: float


class FailedStockResponse(StockResponse):
    """
    Model representing a failed response after attempting to scrape stock data.
    Contains the original request data with None values for timestamp and value.

    Parameters
    ----------
    company_name : str
        Name of the company whose stock data was attempted to be scraped.
    stock_code : str
        Stock code (ticker symbol) of the stock that was attempted to be scraped.
    timestamp : None
        None indicating that the timestamp could not be retrieved
        due to scraping failure.
    value : None
        None indicating that the stock value could not be retrieved
        due to scraping failure.
    """

    timestamp: Literal[None] = None
    value: Literal[None] = None

    model_config = ConfigDict(extra="forbid", frozen=True)
