import logging

def setup_logger():
    """
    Configure logging.
    :return: Logger object.
    """
    logger = logging.getLogger("FileSearchLogger")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()
