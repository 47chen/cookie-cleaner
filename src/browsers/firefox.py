import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from ..utils.system import is_process_running
from .base import BrowserBase

class FirefoxBrowser(BrowserBase):
    """Firefox browser cookie management implementation"""
    
    TABLE_NAME = "moz_cookies"
    COUNT_QUERY = f"SELECT COUNT(*) FROM {TABLE_NAME}"
    SELECT_QUERY = """
        SELECT host, name, path, value, expiry 
        FROM moz_cookies 
        ORDER BY host LIMIT 100
    """

    PROCESS_NAME = "firefox"

    def get_cookie_path(self) -> Optional[Path]:
        """Get Firefox cookie path based on operating system"""
        home = Path.home()
        if sys.platform == "win32":
            base_path = home / "AppData/Roaming/Mozilla/Firefox/Profiles"
        elif sys.platform == "darwin":
            base_path = home / "Library/Application Support/Firefox/Profiles"
        elif sys.platform.startswith("linux"):
            base_path = home / ".mozilla/firefox"
        else:
            self.logger.error(f"Unsupported operating system: {sys.platform}")
            return None

        try:
            # Find default profile
            for folder in base_path.iterdir():
                if folder.name.endswith('.default-release'):
                    return folder / 'cookies.sqlite'
            return None
        except Exception as e:
            self.logger.error(f"Error finding Firefox profile: {str(e)}")
            return None

    def get_cookie_details(self) -> List[Tuple]:
        """Retrieve cookie details from Firefox's database"""
        try:
            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                return []

            # Create temporary copy to avoid locks
            temp_db = cookie_path.parent / 'cookies_temp.sqlite'
            shutil.copy2(cookie_path, temp_db)

            conn = sqlite3.connect(str(temp_db))
            c = conn.cursor()
            c.execute(self.SELECT_QUERY)
            cookies = c.fetchall()
            conn.close()

            temp_db.unlink(missing_ok=True)
            return cookies

        except Exception as e:
            self.logger.error(f"Error reading cookies: {str(e)}")
            return []

    def clean_cookies(self) -> Tuple[bool, int, int]:
        """Clean all Firefox cookies"""
        try:
            if self.is_running():
                raise RuntimeError("Firefox is running")

            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                raise FileNotFoundError("Cookie file not found")

            # Create backup
            backup_path = cookie_path.parent / f"cookies.sqlite.backup_{datetime.now():%Y%m%d_%H%M%S}"
            shutil.copy2(cookie_path, backup_path)

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