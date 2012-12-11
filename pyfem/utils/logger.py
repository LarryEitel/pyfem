import logging
from logging.handlers import TimedRotatingFileHandler
import os

def configure_logging(app):
    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    if app.config.get('LOG_FILE'):
        log_file = app.config['LOG_FILE']
        log_file = os.path.abspath(os.path.expanduser(log_file))
        new_handler = TimedRotatingFileHandler(
            log_file, encoding='bz2')
        if app.config.get('LOG_LEVEL'):
            new_level = app.config['LOG_LEVEL']
            new_level = LEVELS.get(new_level, logging.error)
            new_handler.setLevel(new_level)

        log_format = (
            '-' * 80 + '\n' +
            '%(asctime)-15s\n%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
            '%(message)s\n' +
            '-' * 80
            )
        new_handler.setFormatter(logging.Formatter(log_format))

        app.logger.addHandler(new_handler)