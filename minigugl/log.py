"""Custom Logger implementation based loguru.

Resources:
https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e
https://gist.github.com/nkhitrov/a3e31cfcc1b19cba8e1b626276148c49
https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/#uvicorn-only-version
"""
import logging
import sys
from pprint import pformat

# Type hints with loguru:
# https://loguru.readthedocs.io/en/stable/api/type_hints.html
import loguru
from loguru import logger  # noqa: WPS458
from loguru._defaults import LOGURU_FORMAT  # noqa: WPS436


class InterceptHandler(logging.Handler):
    """Custom handler to integrate with standard lib `logging`.

    Based on example from loguru docs:
    https://loguru.readthedocs.io/en/stable/overview.html
    """

    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record: logging.LogRecord):
        """Pass log record to loguru.

        Args:
            record: A logging.LogRecord instance to be emitted to the logs.
        """
        # Get corresponding loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(
            level,
            record.getMessage(),
        )


def _format_record(
    record: 'loguru.Record',
    log_format: str,
) -> str:
    """Format loguru log record according to specified format.

    Args:
        record: A loguru.Record instance to get formatted.
        log_format: A str with the desired log format.

    Returns:
        A str representing the formatted log entry.

    Uses pprint.pformat() to log any additional data passed in as extra
    payload. Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87}], "count": 1}]
    >>> logger.bind(payload=payload).debug("users payload")
    >>> [   {   'count': 1,
    >>>         'users': [   {'age': 87, 'name': 'Nick'}]}]
    """
    format_string = log_format
    if record.get('extra', {}).get('payload'):
        record['extra']['payload'] = pformat(
            record['extra']['payload'], indent=4, compact=True, width=100,
        )
        format_string = '{0}{1}'.format(
            format_string,
            '<level>{extra[payload]}</level>\n',
        )
    return format_string


def setup_logging(log_level: str, log_format: str = LOGURU_FORMAT):
    """Set up loguru to be the sole logging mechanism.

    Args:
        log_level: A str to set the desired log level.
        log_format: A str for custom log format. Defaults to loguru default.

    Register a custom InterceptHandler based on loguru as sole handler for the
    root logger. Further, remove all registered logger handlers and set
    corresponding loggers to propogate up the the root logger now handled by
    loguru. A custom dict can be passed as payload to the log for debugging
    purposes.
    """
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level.upper())

    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():  # type: ignore
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Configure loguru
    logger.configure(
        handlers=[{
            'sink': sys.stdout,
            'format': lambda record: _format_record(record, log_format),
            'enqueue': True,
            'backtrace': True,
        }])
