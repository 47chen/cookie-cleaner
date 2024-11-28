"""Utility functions for the Browser Cookie Cleaner."""
from .logger import setup_logger
from .system import (
    get_operating_system,
    get_home_directory,
    is_process_running,
    get_temp_directory,
    create_backup_filename
)

__all__ = [
    'setup_logger',
    'get_operating_system',
    'get_home_directory',
    'is_process_running',
    'get_temp_directory',
    'create_backup_filename'
]