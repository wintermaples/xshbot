import logging


class StreamLoggerFactory:

    @staticmethod
    def create(name: str, level):
        log_with_time_formatter = logging.Formatter('%(asctime)s - %(message)s')

        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(log_with_time_formatter)
        handler.setLevel(level)
        logger.setLevel(level)
        logger.addHandler(handler)
        logger.propagate = False
        return logger