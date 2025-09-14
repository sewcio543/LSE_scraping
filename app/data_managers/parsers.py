"""Module containing functions to parse input data into application-specific models."""

import pandas as pd
from pydantic import ValidationError

import app.constants as const
import app.exceptions as exc
from app.models.pydantic_models import StockRequest


def parse_requests(data: pd.DataFrame) -> list[StockRequest]:
    """
    Converts dataframe rows into validated `StockRequest` objects ready for scraping.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing stock request data with
        columns matching `StockRequest` fields.

    Returns
    -------
    list[StockRequest]
        List of validated `StockRequest` objects.
    """

    requests: list[StockRequest] = []

    for _, row in data.iterrows():
        try:
            requests.append(StockRequest(**row.to_dict()))
        except ValidationError as e:
            raise exc.DataValidationError(
                f"Invalid row data: {row.to_dict()} | {e}"
            ) from e

    return requests


def parse_url(stock_info: StockRequest) -> str:
    """
    Constructs the URL for a given stock based on its code and company name.

    Parameters
    ----------
    stock_info : StockRequest
        StockRequest object containing stock_code and company_name.

    Returns
    -------
    str
        Constructed URL for the stock's page on the LSE website.
    """
    url_parts = [
        const.LSEWebsite.BASE_URL,
        const.LSEWebsite.STOCK_ENDPOINT,
        stock_info.stock_code,
        stock_info.company_name.lower().replace(" ", "-"),
    ]
    return "/".join(url_parts)
