"""
Main script to run the LSE stock price scraper.
Configures and initiates the scraping process.

CLI Arguments
----------------
--input: Path to the input CSV file containing stock codes and company names.
--output: Path to the output file where results will be saved.

Scrapes information for provided in input data stocks and saves results in a CSV file
of identical structure as input.
"""

import argparse
from pathlib import Path

import pandas as pd

import app.constants as consts
import app.exceptions as exc
from app.data_managers.output_saver import CSVSaver
from app.data_managers.parsers import parse_requests
from app.data_managers.reader import LSEDataReader
from app.logging import logger
from app.models.pydantic_models import FailedStockResponse, StockResponse
from app.scraping.selenium_utils import get_driver


def main(input_path: Path, output_path: Path, headless: bool = True) -> None:
    """
    Main function to run the scraping process.

    Parameters
    ----------
    input_path : Path
        Path to the input CSV file containing stock codes and company names.
    output_path : Path
        Path to the output file where results will be saved.
    headless : bool, optional
        Whether to run the browser in headless mode (default is True).
    """
    reader = LSEDataReader()
    data = reader.read(input_path)
    requests = parse_requests(data)

    driver = get_driver(headless=headless)
    responses: list[StockResponse] = []

    for request in requests:
        try:
            response = driver.scrape(request)
        except exc.ScrapingError as e:
            logger.error(f"Error scraping {request.stock_code}: {e}")
            response = FailedStockResponse(
                company_name=request.company_name,
                stock_code=request.stock_code,
            )
        responses.append(response)

    driver.quit()

    output = pd.DataFrame([s.model_dump() for s in responses])

    saver = CSVSaver()
    saver.save(data=output, path=output_path)

    logger.info(f"Output saved to {output_path}")


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Scrape LSE stock prices")
    parser.add_argument("--input", type=Path, required=True, help="Path to input CSV")
    parser.add_argument("--output", type=Path, required=True, help="Output file")
    parser.add_argument(
        "--show", action="store_true", help="Run browser in visible mode"
    )
    args = parser.parse_args()

    main(input_path=args.input, output_path=args.output, headless=not args.show)
