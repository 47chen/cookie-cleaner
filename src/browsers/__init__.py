"""Browser implementations for cookie cleaning."""
from .base import BrowserBase
from .chrome import ChromeBrowser
from .firefox import FirefoxBrowser

__all__ = ['BrowserBase', 'ChromeBrowser', 'FirefoxBrowser']