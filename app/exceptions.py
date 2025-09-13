"""Module defining custom exceptions for the application."""


class LSEError(Exception):
    """Base exception for all errors in the LSE scraper project."""


class DataValidationError(LSEError):
    """Raised when input data fails validation."""


class ScrapingError(LSEError):
    """Raised when an error occurs during the scraping process."""


class PageLoadError(LSEError):
    """
    Raised when a web page fails to load properly for one of the reasons:
    - Stock url was invalid and driver was redirected
    - Network issues
    - Website structure changed and informations cannot be found
    """
