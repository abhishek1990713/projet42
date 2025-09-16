
import logging
import sys


def setup_logger():
    """
    Configure a global logger with console and file output.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("feedback_app")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # File handler
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Global logger
logger = setup_logger()
