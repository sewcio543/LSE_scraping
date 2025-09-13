"""
Module defining soupsavvy models or selectors for scraping stock data.
"""

from soupsavvy import ClassSelector, IdSelector, TypeSelector
from soupsavvy.models import BaseModel
from soupsavvy.operations import Operation, Text

import app.constants as consts


class StockScraperModel(BaseModel):
    """
    Model for scraping all necessary data about a stock from LSE website.
    Blueprint for finding inormation on the page.

    Parameters
    ----------
    value : float
        Scraped stock value.
    timestamp : str
        Timestamp on LSE website when scraped stock value was last updated.
    """

    __scope__ = IdSelector(consts.STOCK_SCOPE_ID)

    value = (
        ClassSelector(consts.PRICE_TAG_CLASS)
        | Text()
        | Operation(str.replace, ",", "")
        | Operation(float)
    )
    timestamp = (
        ClassSelector(consts.TIMESTAMP_ANCESTOR_CLASS)
        >> TypeSelector(consts.TIMESTAMP_TAG_TYPE)
    ) | Text()
