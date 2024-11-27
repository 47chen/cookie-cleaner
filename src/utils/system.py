import sys
import psutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def get_operating_system() -> str:
    """Get the current operating system name"""
    if sys.platform == "win32":
        return "Windows"
    elif sys.platform == "darwin":
        return "macOS"
    elif sys.platform.startswith("linux"):
        return "Linux"
    else:
        return "Unknown"

def get_home_directory() -> Path:
    """Get user's home directory"""
    return Path.home()

def is_process_running(process_name: str) -> bool:
    """Check if a process is running by name"""
    try:
        for proc in psutil.process_iter(['name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False
    except Exception as e:
        logger.error(f"Error checking process {process_name}: {str(e)}")
        return False

def get_temp_directory() -> Path:
    """Get system temporary directory"""
    return Path(sys.prefix) / "temp"

def create_backup_filename(original_path: Path, prefix: str = "backup") -> Path:
    """Create a backup filename with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return original_path.parent / f"{prefix}_{timestamp}_{original_path.name}"