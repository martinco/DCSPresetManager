"""
Global logging handler
"""

import logging
import sys


LOG_FORMATTER = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s')


def add_file_logger(filepath):
    """
    Add logfile handler
    """

    file = logging.FileHandler(filepath)
    file.setFormatter(LOG_FORMATTER)
    logging.root.addHandler(file)


def add_stdout_logger():
    """
    Add stream handler to stdout
    """

    stream = logging.StreamHandler()
    stream.setFormatter(LOG_FORMATTER)
    logging.root.addHandler(stream)


def get(name=None):
    """
    Returns a standard logger named: dcs_preset_manager.<module>
    """

    if name is None:
        try:
            frame_globals = sys._getframe(1).f_globals  # noqa
            name = frame_globals.get("__name__")
        except Exception as e:
            logger = logging.root
            logger.warning('Could not get logger for %s: %s', type(e).__name__, e)
            return logger

    return logging.getLogger(name)
