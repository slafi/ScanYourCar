import sys
import logging

from logging import handlers


## Create and return a logging object
def get_logger(label):

    '''This function creates and returns a logging object

        :param label: The label that will be added to the name of the log file    
    '''

    logger = logging.getLogger(label)
    logger.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s [%(relativeCreated)5d - %(name)-5s] [%(levelname)-6s] => %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    logger.addHandler(ch)

    fh = handlers.RotatingFileHandler('./log_{}.txt'.format(label), maxBytes=(1048576*10), backupCount=7)
    fh.setFormatter(format)
    logger.addHandler(fh)

    return logger