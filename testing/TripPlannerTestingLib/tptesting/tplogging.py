import logging

logs = None

class MemoryLoggingHandler(logging.Handler):

    def __new__(cls):
        global logs
        if logs is not None:
            return logs

        logs = logging.Handler.__new__(cls)
        return logs

    def __init__(self):
        logging.Handler.__init__(self)
        self.messages = list()

    def emit(self, record):
        self.messages.append(record)

    def flush(self):
        self.messages = list()

    def close(self):
        self.flush()
        logging.Handler.close(self)


