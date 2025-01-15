import logging
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    filename=f"./logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    encoding="utf-8",
    format="%(asctime)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logger = logging.getLogger("application_logger")


def log(message, console=False):
    if console:
        print(message)
    logger.info(message)


def log_chat(chat_history, console=False):
    logger.info("CHAT COMPLETION:")
    for message in chat_history:
        if console:
            message.pretty_print()
        logger.info(message.pretty_repr())


def log_error(message):
    print(f"Error: {message}")
    logger.error(message)
