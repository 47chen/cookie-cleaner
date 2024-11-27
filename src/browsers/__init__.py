"""Browser implementations for cookie cleaning."""
from .base import BrowserBase
from .chrome import ChromeBrowser
from .firefox import FirefoxBrowser
from .edge import EdgeBrowser

__all__ = ['BrowserBase', 'ChromeBrowser', 'FirefoxBrowser', 'EdgeBrowser']