import logging
import os
import datetime as dt


class LastRecordHandler(logging.Handler):
    """
    Class that implements buffer for last X logging messages
    """
    MAX_COUNT = 7

    def __init__(self):
        """
        Initialize logging handler and clear all records
        """
        logging.Handler.__init__(self)
        self.records = []

    def emit(self, record):
        """
        Append emitted record to list of the most recent messages
        :param record: Current record
        :return: None
        """
        self.records.append(record)
        if len(self.records) > self.MAX_COUNT:
            self.records.pop(0)

    def get_record(self):
        """
        Retrieve the status message of last X records
        :return: String message of the X most recent records
        """
        ret = "STATUS WINDOW \n(from oldest to newest)"
        for rec in self.records:
            ret += '\n\n' + rec.asctime + ' - ' + rec.getMessage()
        return ret

    def get_one_liner(self):
        """
        Retrieve only the last record
        :return: String message with one most recent record
        """
        rec = self.records[-1]
        return rec.asctime + ' - ' + rec.getMessage()


class AppLogging:
    """
    Logging class that stores info messages into log file
    """
    LOG_DIRECTORY = 'log/'
    FILE_NAME = dt.datetime.now().strftime("%Y-%m-%d-%H-%M.log")

    def __init__(self, level=logging.INFO):
        """
        Create new log file and set all loggers and formatter
        :param level: Default logging level
        """
        if not os.path.exists(self.LOG_DIRECTORY):
            os.makedirs(self.LOG_DIRECTORY)

        # Formatter for logging into file and console
        logger = logging.getLogger()
        logger.setLevel(level)
        fh = logging.FileHandler(self.LOG_DIRECTORY + self.FILE_NAME)
        fh.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(module)s:%(lineno)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        self.lrl = LastRecordHandler()
        logger.addHandler(self.lrl)

        self.log = logging.getLogger()
        self.log.info('Application started')

        self.head = []
        self.values = []

    def report_add(self, head, value):
        """
        Add new value into report table
        :param head: Heading of the table column
        :param value: Value
        :return: None
        """
        self.head.append(head)
        self.values.append(value)

    def write_report(self, name):
        """
        Write accumulated report into file - append
        :param name: Name of the file
        :return: None
        """
        if not os.path.exists(self.LOG_DIRECTORY):
            os.makedirs(self.LOG_DIRECTORY)
        line = ' | '.join(map(str, self.values))
        with open(self.LOG_DIRECTORY + '/' + name, 'a+', encoding='utf-8-sig') as f:
            f.seek(0, 2)
            val = f.tell()
            if val == 0:
                header = ' | '.join(map(str, self.head))
                f.write('| ' + header + ' |\n')
            f.write('| ' + line + ' |\n')
            f.close()


