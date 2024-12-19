import logging
from datetime import datetime

logger = None


def configure_logger():
    global logger
    if logger is None:
        # Create a logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Create a handler for console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Create a handler for file logging
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = f"log_{current_datetime}.log"
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
