import logging
from datetime import datetime

class Logger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            filename=f"./logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log",
            encoding="utf-8",
            format="%(asctime)s - %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )
        logger = logging.getLogger(__name__)
        self.logger = logger
        
    def log(self, message, console=False):
        if console:
            print(message)
        self.logger.info(message)

    def log_error(self, message):
        print(f"Error: {message}")
        self.logger.error(message)