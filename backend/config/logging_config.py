"""
Logging configuration for the Sports Prophet application.
"""
import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger for the application.
    
    Args:
        level: Logging level (default: INFO)
        log_format: Custom log format string
        
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Create application logger
    logger = logging.getLogger("sports_prophet")
    logger.setLevel(level)
    
    # Reduce verbosity of third-party loggers
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    logging.getLogger("pyspark").setLevel(logging.WARNING)
    
    return logger


# Create default logger
logger = setup_logging()
