import os
import click
import logging.config
import logging


class ColorConsoleFormatStyle(logging.StrFormatStyle):
    colors = {
        'error': dict(fg='red'),
        'exception': dict(fg='red'),
        'critical': dict(fg='red', bold=True),
        'debug': dict(fg='blue'),
        'warning': dict(fg='yellow'),
        'info': dict(fg='green'),
    }

    def format(self, record):
        level = record.levelname.lower()
        fmt = self._fmt
        if level in self.colors:
            prefix = click.style("==> {module:11}[{levelname:^8}]: ", **self.colors[level])
            fmt = prefix + self._fmt
        return fmt.format(**record.__dict__)

    @property
    def fmt(self):
        return self._fmt


class ColorConsoleFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None, style=None):
        super().__init__(fmt, datefmt, "{")
        self._style = ColorConsoleFormatStyle(fmt)
        self._fmt = self._style.fmt


def configure_logging(verbose):
    logging.getLogger('boto3').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('paramiko').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)

    log_level = get_log_level(verbose)
    config = {
        "version": 1,
        "formatters": {
            "console": {
                "class": "greengold.logging_config.ColorConsoleFormatter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
                "formatter": "console",
            },
        },
        "loggers": {
            "greengold": {
                "handlers": ["console"],
                "level": log_level
            }
        },
    }
    logging.config.dictConfig(config)


def get_log_level(verbose):
    if verbose > 1:
        return logging.DEBUG
    elif verbose == 1:
        return logging.INFO
    else:
        return os.environ.get("LOG_LEVEL", logging.ERROR)
