"""
Main script to run the LSE stock price scraper.
Configures and initiates the scraping process.

CLI Arguments
----------------
--input: Path to the input CSV file containing stock codes and company names.
--output: (Optional) Path to the output folder. Default is 'output'.
--name: (Optional) Base name for the output file. Default is 'lse_stocks'.
--timestamp: (Optional) If provided, includes a timestamp in the output filename.

Scrapes information for provided in input data stocks and saves results in a CSV file
of identical structure as input.
"""

import argparse
from pathlib import Path

import pandas as pd

import app.constants as const
from app.data_managers.output_saver import CSVSaver
from app.data_managers.parsers import parse_requests
from app.data_managers.reader import LSEDataReader
from app.scraping.selenium_utils import get_driver


def main(
    input_path: Path,
    output_folder: Path,
    file_name: str,
    include_timestamp: bool = True,
) -> None:
    """
    Main function to run the scraping process.

    Parameters
    ----------
    input_path : Path
        Path to the input CSV file containing stock codes and company names.
    output_folder : Path
        Path to the output folder where results will be saved.
    file_name : str
        Base name for the output file.
    include_timestamp : bool, optional
        Whether to include a timestamp in the output filename, by default True.
    """
    reader = LSEDataReader()
    data = reader.read(input_path)
    requests = parse_requests(data)

    driver = get_driver()
    responses = driver.scrape(requests)

    output = pd.DataFrame([s.model_dump() for s in responses])

    saver = CSVSaver(include_timestamp=include_timestamp, file_name=file_name)
    saver.save(output, output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape LSE stock prices")
    parser.add_argument("--input", type=Path, required=True, help="Path to input CSV")
    parser.add_argument(
        "--output",
        type=Path,
        required=False,
        help="Output folder",
        default=const.DEFAULT_OUTPUT_FOLDER,
    )
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="Output file name",
        default=const.DEFAULT_OUTPUT_FILE_NAME,
    )
    parser.add_argument(
        "--timestamp",
        action="store_true",
        help="Include timestamp in output filename",
    )
    args = parser.parse_args()

    main(
        input_path=args.input,
        output_folder=args.output,
        file_name=args.name,
        include_timestamp=args.timestamp,
    )
