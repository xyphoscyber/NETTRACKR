import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

class Logger:
    def __init__(self, config):
        self.config = config
        self.log_dir = Path("logs")
        self.setup_logger()

    def setup_logger(self):
        """Set up the logger with configuration"""
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)

        log_file = self.log_dir / "nettrackr.log"
        log_level = getattr(logging, self.config.get("logging", {}).get("level", "INFO"))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Set up rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.get("logging", {}).get("max_size_mb", 10) * 1024 * 1024,
            backupCount=self.config.get("logging", {}).get("backup_count", 5)
        )
        file_handler.setFormatter(formatter)

        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    def get_logger(self, name):
        """Get a logger instance with the specified name"""
        return logging.getLogger(name)

class LoggerDecorator:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            self.logger.debug(f"Starting {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"Completed {func.__name__} in {datetime.now() - start_time}")
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
