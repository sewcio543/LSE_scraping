import argparse
from pathlib import Path

import pandas as pd

import app.constants as const
from app.models.pydantic_models import StockRequest
from app.output_saver import CSVSaver
from app.reader import LSEDataReader
from app.selenium_utils import get_driver


def main(
    input_path: Path,
    output_folder: Path,
    file_name: str,
    include_timestamp: bool = True,
) -> None:
    reader = LSEDataReader()
    data = reader.read(input_path)

    requests = list(data.apply(lambda row: StockRequest(**row.to_dict()), axis=1))  # type: ignore

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
        default=Path("output"),
    )
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="Output file name",
        default=const.OUTPUT_FILE_NAME,
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
