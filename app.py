from explorer import explorer
from explorer import utils
from explorer import logger

import time
import sys


if __name__ == "__main__":

    ## Clear console
    utils.clear_console()

    # Get logger
    log = logger.get_logger('pid_explorer')

    ## Create explorer object
    cexplorer = explorer.Explorer(command_file = "./explorer/commands.json", output_file = "./output.txt")
    
    ## Attempts to connect to the car
    cexplorer.connect()

    ## Keep checking connection status until connected to the car or timeout expired
    timeout = 15
    interval = 0.1
    counter = 0
    isNotConnected = True
    while(isNotConnected and counter * interval < timeout):
        if cexplorer.check_connection():
            isNotConnected = False
            break

        log.debug('Attempt #{}: => status: {}'.format(counter, cexplorer.connection.status))
        counter += 1
        time.sleep(interval)

    ## If connection established, run the test
    if(isNotConnected):
        log.debug('Connection timeout...')
        sys.exit()
    else:
        ## Querying the car to get the supported commands
        log.info('Checking supported commands...')
        rcode = cexplorer.check_supported_commands()

        ## Querying the car to get current data for each supported command
        log.info('Fetching data from the car...')
        if rcode == 0:
            cexplorer.run_supported_commands()
        else:
            log.error('Could not retrieve any data from the car because the list of supported commands is empty!')

        ## Closing connection to the car and exiting
        log.info('Disconnecting...')
        cexplorer.disconnect()
