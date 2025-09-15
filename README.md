# 📈 London Stock Exchange Data Extractor

## 📌 Problem Description

Investors or analysts otften need up-to-date stock prices from [London Stock Exchange](<https://www.londonstockexchange.com/>), doing it manually is time-consuming and error-prone.

This tool automates the process: given a list of stocks it extracts their most recent values from the exchange webite andsaves them in structured format.

## 🎯 Objective

- Input: CSV file with stock `company-name` and `stock-code`
- Output: CSV file with the following columns:
  - `company-name`
  - `stock-code`
  - `price`
  - `timestamp` (time from LSE, not script execution time)

## ✅ Requirements

- User provides a CSV file containing stock codes and company names.
- Script navigates to each stock’s LSE page and scrapes:
  - Price → from `span.price`
  - Timestamp → from `.delay span`
- Results are saved in a CSV file with identical structure plus scraped values.
- If a stock page fails to load or data cannot be extracted, the stock still appears in the output file, but timestamp and price will be empty.

## 🔍 Assumptions

- Stock page URL format:

```ruby
https://www.londonstockexchange.com/stock/{STOCK_CODE}/{COMPANY_NAME}
```

Example: `https://www.londonstockexchange.com/stock/GLEN/glencore-plc`

- Company name in URL is lowercase with spaces replaced by hyphens.
- Website structure is stable.

## 🛠 Tools

- `selenium` - browser automation & dynamic page loading
- `pandas` - CSV reading/writing
- [`sopusavvy`](https://pypi.org/project/soupsavvy/) - HTML data extraction
- `pydantic` - input/output data validation
- `pytest` - unit and integration tests

## 🚀 Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

2. Prepare valid input CSV file or use example provided in `data/LSE_inut.csv`.

```csv
company-name,stock-code
Glencore plc,GLEN
Xylion Devices,XD
```

3. Run the script:

```bash
python -m app.run --input {path_to_input_file} --output {path_to_output_file}
```

4. Output

```csv
company-name,stock-code,price,timestamp
Glencore plc,GLEN,160.35,14.09.25 13:03:33 BST
Xylion Devices,XD,,
```

🎉 **Enjoy!**
