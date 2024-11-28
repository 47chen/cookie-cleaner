import sys
import os
import sqlite3
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from ..utils.system import is_process_running
from .base import BrowserBase

class ChromeBrowser(BrowserBase):
    """Chrome browser cookie management implementation with enhanced process handling"""
    
    TABLE_NAME = "cookies"
    COUNT_QUERY = f"SELECT COUNT(*) FROM {TABLE_NAME}"
    SELECT_QUERY = """
        SELECT host_key, name, path, value, expires_utc 
        FROM cookies 
        ORDER BY host_key LIMIT 100
    """

    PROCESS_NAMES = [
        "Google Chrome",
        "chrome",
        "Chrome",
        "Google Chrome Helper",
        "Chrome Helper",
        "chromedriver",
        "Chrome Canary",
        "chromium",
    ]

    def force_quit_chrome(self) -> bool:
        """Force quit all Chrome-related processes on macOS"""
        try:
            # First attempt: Use pkill
            for proc in self.PROCESS_NAMES:
                subprocess.run(['pkill', '-f', proc], check=False)

            # Second attempt: Use osascript to force quit Chrome
            apple_script = """
                tell application "Google Chrome" to quit
                delay 2
                do shell script "killall -9 'Google Chrome' 'Google Chrome Helper' 'Chrome' 'chromedriver'"
            """
            subprocess.run(['osascript', '-e', apple_script], check=False)

            # Wait for processes to terminate
            import time
            time.sleep(2)
            
            return not self.is_running()
            
        except Exception as e:
            self.logger.error(f"Error force quitting Chrome: {str(e)}")
            return False

    def clear_chrome_cache(self) -> bool:
        """Clear Chrome cache directories"""
        try:
            home = Path.home()
            cache_paths = []
            
            if sys.platform == "darwin":
                cache_paths = [
                    home / "Library/Caches/Google/Chrome/Default/Cache",
                    home / "Library/Application Support/Google/Chrome/Default/Cache",
                    home / "Library/Application Support/Google/Chrome/Default/Code Cache",
                    home / "Library/Application Support/Google/Chrome/Default/GPUCache",
                    home / "Library/Application Support/Google/Chrome/Default/Service Worker/CacheStorage",
                ]

            for cache_path in cache_paths:
                if cache_path.exists():
                    try:
                        if cache_path.is_dir():
                            shutil.rmtree(cache_path, ignore_errors=True)
                        else:
                            cache_path.unlink(missing_ok=True)
                        self.logger.info(f"Cleared cache: {cache_path}")
                    except Exception as e:
                        self.logger.error(f"Error clearing cache {cache_path}: {str(e)}")

            return True

        except Exception as e:
            self.logger.error(f"Error clearing Chrome cache: {str(e)}")
            return False

    def clean_cookies(self) -> Tuple[bool, int, int]:
        """Clean all Chrome cookies with enhanced process handling"""
        try:
            if self.is_running():
                self.logger.info("Attempting to force quit Chrome...")
                if not self.force_quit_chrome():
                    raise RuntimeError("Unable to terminate Chrome processes")

            # Clear cache first
            self.clear_chrome_cache()

            cookie_path = self.get_cookie_path()
            if not cookie_path or not cookie_path.exists():
                raise FileNotFoundError("Cookie file not found")

            # Create backup before cleaning
            backup_path = cookie_path.parent / f"Cookies.backup_{datetime.now():%Y%m%d_%H%M%S}"
            shutil.copy2(cookie_path, backup_path)

            initial_count = self.get_cookie_count()
            
            # Try to clean cookies
            conn = sqlite3.connect(str(cookie_path))
            c = conn.cursor()
            c.execute(f"DELETE FROM {self.TABLE_NAME}")
            conn.commit()
            conn.close()

            final_count = self.get_cookie_count()
            
            if initial_count == final_count:
                self.logger.warning("Cookies count unchanged after cleaning")
            else:
                self.logger.info(f"Successfully cleaned {initial_count - final_count} cookies")

            return True, initial_count, final_count

        except Exception as e:
            self.logger.error(f"Error cleaning cookies: {str(e)}")
            return False, 0, 0

    def is_running(self) -> bool:
        """Enhanced check for Chrome processes"""
        try:
            # Use ps command on macOS for more thorough process checking
            if sys.platform == "darwin":
                result = subprocess.run(
                    ['ps', 'aux'], 
                    capture_output=True, 
                    text=True
                )
                output = result.stdout.lower()
                
                for proc in self.PROCESS_NAMES:
                    if proc.lower() in output:
                        self.logger.info(f"Found running Chrome process: {proc}")
                        return True
                        
            # Fallback to basic process checking
            for proc in self.PROCESS_NAMES:
                if is_process_running(proc):
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking Chrome processes: {str(e)}")
            return True  # Fail safe: assume running if check fails

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