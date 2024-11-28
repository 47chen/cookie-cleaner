import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from ..utils.system import is_process_running
from .base import BrowserBase

class EdgeBrowser(BrowserBase):
    """Microsoft Edge browser cookie management implementation"""
    
    TABLE_NAME = "cookies"
    COUNT_QUERY = f"SELECT COUNT(*) FROM {TABLE_NAME}"
    SELECT_QUERY = """
        SELECT host_key, name, path, value, expires_utc 
        FROM cookies 
        ORDER BY host_key LIMIT 100
    """

    PROCESS_NAMES = ["msedge", "Microsoft Edge"]

    def get_cookie_path(self) -> Optional[Path]:
        """Get Edge cookie path based on operating system"""
        home = Path.home()
        if sys.platform == "win32":
            base_path = home / "AppData/Local/Microsoft/Edge/User Data/Default"
        elif sys.platform == "darwin":
            base_path = home / "Library/Application Support/Microsoft Edge/Default"
        elif sys.platform.startswith("linux"):
            base_path = home / ".config/microsoft-edge/Default"
        else:
            self.logger.error(f"Unsupported operating system: {sys.platform}")
            return None

        cookie_path = base_path / "Cookies"
        return cookie_path if cookie_path.exists() else None

    def get_cookie_details(self) -> List[Tuple]:
        """Retrieve cookie details from Edge's database"""
        try:
            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                return []

            # Create temporary copy to avoid database locks
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
            self.logger.error(f"Error reading Edge cookies: {str(e)}")
            return []

    def clean_cookies(self) -> Tuple[bool, int, int]:
        """Clean all Edge cookies"""
        try:
            if self.is_running():
                raise RuntimeError("Edge is running")

            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                raise FileNotFoundError("Cookie file not found")

            # Create backup
            backup_path = cookie_path.parent / f"Cookies.backup_{datetime.now():%Y%m%d_%H%M%S}"
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
            self.logger.error(f"Error cleaning Edge cookies: {str(e)}")
            return False, 0, 0

    def is_running(self) -> bool:
        """Check if Edge is running"""
        for process_name in self.PROCESS_NAMES:
            if is_process_running(process_name):
                return True
        return False 