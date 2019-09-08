from os import system, name
from .logger import get_logger
import sys
import logging


log = logging.getLogger('pid_explorer')


def clear_console():

    '''This function clears the console
    '''

    # for windows
    if name == 'nt': 
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear')


def write_to_file(output_file, mode, text=''):
    """ Writes a text string to a file """
    try:
        ## Open output text file
        fid = open(output_file,mode)

        fid.write(text)

        fid.close()    
        
    except Exception as inst:
        log.error("Exception: {}".format(inst))
        sys.exit()