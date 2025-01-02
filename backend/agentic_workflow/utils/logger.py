import logging
import logging.handlers
import functools
import sys
import os


def log_setup():
    # Configure log handlers
    file_handler = logging.handlers.RotatingFileHandler(
        "app.log", maxBytes=10 * 1024 * 1024, backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(thread)d %(threadName)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Configure logger
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(os.getenv("LOG_LEVEL") or logging.INFO)

    package_logger = logging.getLogger("stream2sentence")
    package_logger.setLevel(logging.ERROR)
    package_logger.addHandler(stream_handler)


def log(level=logging.DEBUG):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.log(
                level,
                f"Calling function {func.__name__} from module {func.__module__} with args {args} and kwargs {kwargs}",
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
