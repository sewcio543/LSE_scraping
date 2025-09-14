from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver


def get_driver_options() -> Options:
    """Set up a single Chrome driver for the entire session."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--silent")
    return options


def insert(html: str, driver: WebDriver) -> None:
    """Insert HTML content into the selenium browser."""
    driver.execute_script("document.body.innerHTML = arguments[0];", html)
