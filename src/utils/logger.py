import os
import logging
import glob
from datetime import datetime
from pathlib import Path
import sys

def cleanup_old_logs(log_dir: str, max_files: int = 5) -> None:
    """
    Clean up old log files when the number of files exceeds the maximum.
    
    Args:
        log_dir: Directory containing log files
        max_files: Maximum number of log files to keep (default: 5)
    """
    try:
        # Get all log files
        log_files = glob.glob(os.path.join(log_dir, "cookie_cleaner_*.log"))
        
        # If number of files is within limit, do nothing
        if len(log_files) <= max_files:
            return
            
        # Sort files by modification time (oldest first)
        log_files.sort(key=lambda x: os.path.getmtime(x))
        
        # Calculate how many files to delete
        files_to_delete = len(log_files) - max_files
        
        # Delete oldest files
        for i in range(files_to_delete):
            try:
                os.remove(log_files[i])
                logging.info(f"Deleted old log file: {log_files[i]}")
            except Exception as e:
                logging.error(f"Error deleting log file {log_files[i]}: {str(e)}")
                
    except Exception as e:
        logging.error(f"Error during log cleanup: {str(e)}")

def setup_logger():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Clean up old logs before creating new one
    cleanup_old_logs(log_dir)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"cookie_cleaner_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log system information
    logging.info("Starting Browser Cookie Cleaner")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Operating System: {sys.platform}")
    
    return logging.getLogger(__name__)