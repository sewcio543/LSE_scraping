"""
Module defining Pydantic models representing scraping request and response structures.
Used for data validation and serialization.

Can be used for easy integration with API frameworks if needed.
"""

from pydantic import BaseModel


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

    company_name: str
    stock_code: str


# TODO: think what to do if request fails
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
    timestamp : str | None
        Timestamp indicated by LSE website when scraped stock value was last updated.
        None if scraping failed.
    value : float | None
        Scraped stock value. None if scraping failed.
    """

    company_name: str
    stock_code: str
    timestamp: str | None = None
    value: float | None = None
