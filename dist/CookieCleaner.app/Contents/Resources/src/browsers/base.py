from abc import ABC, abstractmethod
from pathlib import Path
import logging
import sqlite3
from typing import List, Tuple, Optional

class BrowserBase(ABC):
    """Abstract base class for browser cookie management"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_cookie_path(self) -> Optional[Path]:
        """Get the path to the cookie database"""
        pass

    @abstractmethod
    def get_cookie_details(self) -> List[Tuple]:
        """Get details of stored cookies"""
        pass

    @abstractmethod
    def clean_cookies(self) -> Tuple[bool, int, int]:
        """Clean all cookies. Returns (success, initial_count, final_count)"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Check if the browser is currently running"""
        pass

    def get_cookie_count(self) -> int:
        """Get the total number of cookies"""
        try:
            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                return 0
            
            conn = sqlite3.connect(str(cookie_path))
            c = conn.cursor()
            c.execute(self.COUNT_QUERY)
            count = c.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            self.logger.error(f"Error counting cookies: {str(e)}")
            return -1