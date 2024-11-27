import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    log_file = log_dir / f"cookie_cleaner_{datetime.now():%Y%m%d_%H%M%S}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with detailed formatting
            logging.FileHandler(log_file),
            # Stream handler with simpler formatting
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log system information at startup
    logger = logging.getLogger(__name__)
    logger.info("Starting Browser Cookie Cleaner")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Operating System: {sys.platform}")
    
    return logger