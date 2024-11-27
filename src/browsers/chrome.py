import sys
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
from ..utils.system import is_process_running
from .base import BrowserBase

class ChromeBrowser(BrowserBase):
    """Chrome browser cookie management implementation"""
    
    TABLE_NAME = "cookies"
    COUNT_QUERY = f"SELECT COUNT(*) FROM {TABLE_NAME}"
    SELECT_QUERY = """
        SELECT host_key, name, path, value, expires_utc 
        FROM cookies 
        ORDER BY host_key LIMIT 100
    """

    PROCESS_NAME = "chrome" # Define the process name as a class constant

    def get_cookie_path(self) -> Optional[Path]:
        """Get Chrome cookie path based on operating system"""
        home = Path.home()
        if sys.platform == "win32":
            return home / "AppData/Local/Google/Chrome/User Data/Default/Cookies"
        elif sys.platform == "darwin":
            return home / "Library/Application Support/Google/Chrome/Default/Cookies"
        elif sys.platform.startswith("linux"):
            return home / ".config/google-chrome/Default/Cookies"
        else:
            self.logger.error(f"Unsupported operating system: {sys.platform}")
            return None

    def get_cookie_details(self) -> List[Tuple]:
        """Retrieve cookie details from Chrome's database"""
        try:
            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                return []

            conn = sqlite3.connect(str(cookie_path))
            c = conn.cursor()
            c.execute(self.SELECT_QUERY)
            cookies = c.fetchall()
            conn.close()
            return cookies
        except Exception as e:
            self.logger.error(f"Error reading cookies: {str(e)}")
            return []

    def clean_cookies(self) -> Tuple[bool, int, int]:
        """Clean all Chrome cookies"""
        try:
            if self.is_running():
                raise RuntimeError("Chrome is running")

            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                raise FileNotFoundError("Cookie file not found")

            initial_count = self.get_cookie_count()
            
            conn = sqlite3.connect(str(cookie_path))
            c = conn.cursor()
            c.execute(f"DELETE FROM {self.TABLE_NAME}")
            conn.commit()
            conn.close()

            final_count = self.get_cookie_count()
            return True, initial_count, final_count

        except Exception as e:
            self.logger.error(f"Error cleaning cookies: {str(e)}")
            return False, 0, 0

    def is_running(self) -> bool:
        """Check if Chrome is running"""
        return is_process_running(self.PROCESS_NAME)