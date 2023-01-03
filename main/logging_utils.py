import time
import datetime
import logging


class _DeltaTiming:
    def __init__(self):
        self.timestamp = time.time()

    def get_reset(self):
        self.timestamp = time.time()

    def get_init(self):
        init = datetime.datetime.fromtimestamp(self.timestamp)
        init = init.strftime("%H:%M:%S,%f")[:-3]

        return init

    def get_duration(self):
        duration = time.time()-self.timestamp
        duration = datetime.datetime.utcfromtimestamp(duration)
        duration = duration.strftime("%H:%M:%S,%f")[:-3]

        return duration


class BlockTimer:
    def __init__(self, logger, name):
        self.logger = logger
        self.name = name
        self.timer = _DeltaTiming()

    def __enter__(self):
        self.timer.get_reset()
        self.logger.info(self.name + " : enter : timing")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        duration = self.timer.get_duration()
        self.logger.info(self.name + " : exit : " + duration)


class DeltaTimeFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.timer = _DeltaTiming()

    def format(self, record):
        record.init = self.timer.get_init()
        record.duration = self.timer.get_duration()

        msg = super().format(record)

        return msg


def get_logger(name="root", level=logging.INFO):
    fmt = DeltaTimeFormatter('%(duration)s : %(asctime)s : %(name)-10s: %(levelname)-12s : %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(fmt)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
