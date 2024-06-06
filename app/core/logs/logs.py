import logging


def _init_logger(name: str):
    # logger configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(name)
    return logger


def get_logger(name: str = "BE"):
    return _init_logger(name)


logger = get_logger()
