from .logger import get_logger
from .utils import write_to_file

import json
import logging
import time
import obd
import datetime

### Initialize logger for the module
log = logging.getLogger('pid_explorer')


class Explorer:


    def __init__(self, command_file = "./commands.json", output_file = "./output.txt", verbose=False):
        self.output_file = output_file
        self.commands = []
        self.supported_commands = []
        self.connection = None
        self.Enabled = False

        try:
            log.info('Loading standard OBD-II commands from "{}"...'.format(command_file))
            with open(command_file) as json_file:  
                data = json.load(json_file)
                
                counter = 0
                for p in data:
                    self.commands.append(p['command'])
                    counter += 1
                    if verbose:
                        log.info('{} -> {}'.format(p['command'], p['description']))
                
                log.info('{} OBD-II commands loaded.'.format(counter))
       
        except Exception as inst:
            log.error("Exception: {}".format(inst))


    def connect(self):
        """ Attempts to connect to the ELM327 
            :returns int: 0 if the connection is established, -1 otherwise
        """        
        try:
            self.connection = obd.OBD()
            #self.connection = obd.Async() # auto-connects asynchronously to USB or RF port
            return 0
        except Exception as inst:
            log.error("Exception: {}".format(inst))
            return -1


    def check_connection(self):
        """ Checks if the connection is already established. Returns boolean or None if exception 
            :returns Boolean: True if the connection is already established, False if the connection is not established, None if an exception has occured
        """
        try:

            if(self.connection.status() == obd.OBDStatus.CAR_CONNECTED):
                log.debug("Explorer is now connected to the car!")
                self.Enabled = True
                return True
            else:
                log.debug("Explorer could not connect to the car!")
                self.Enabled = False
                return False

        except Exception as inst:
            log.error("Exception: {}".format(inst))
            return None


    def disconnect(self):
        """ Closes the established connection to the ELM327 
            :returns Boolean: True if the connection is closed successfully, False if the connection already not alive/established, None if an exception has occured
        """
        try:

            if(self.connection.status() == obd.OBDStatus.CAR_CONNECTED):
                self.connection.close()
                self.Enabled = True
                log.debug("Connection to the car is closed!")
                return True
            else:
                log.debug("Connection to the car is already not alive!")
                return False

        except Exception as inst:
            log.error("Exception: {}".format(inst))
            return None


    def check_supported_commands(self):

        """ Runs through the input list of commands and Checks which among them are suported by the car 
            :returns int: 0 if success, -1 if the list of commands is empty, -2 if no connection found, -3 if an exception has occured
        """

        self.supported_commands = []

        try:

            if(self.commands == [] or self.commands == None):
                log.error('No commands to apply!')
                return -1
            elif(self.connection == None):
                log.error('Connection to the car not found!')
                return -2
            else:

                output = []
                self.supported_commands=[]
                output.append('-----------------------------------------------\n')
                output.append('\tScanYourCar version 1.0\n')
                output.append('\tTest run on {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                output.append('-----------------------------------------------\n')
                
                count = 0
                ## Check commands one by one
                for cmd in self.commands:
                    try:
                        is_supported = self.connection.supports(obd.commands[cmd])

                        if is_supported == True:
                            output.append("{} .............. [OK]\r\n".format(cmd))
                            self.supported_commands.append(cmd)
                            count += 1
                        else:
                            output.append("{} .............. [NOT SUPPORTED]\r\n".format(cmd))

                        time.sleep(0.1)

                    except Exception as inst:
                        log.error("Exception: {}".format(inst))
                    
                output.append('-----------------------------------------------\n')
                output.append('Test results: {} commands are supported.\n'.format(count))
                output.append('-----------------------------------------------\n')
                output_str = ''.join(output)
                write_to_file(self.output_file, "w", output_str)                    

            return 0

        except Exception as inst:
            log.error("Exception: {}".format(inst))
            return -3


    def run_supported_commands(self):

        """ Attempts to sequentially run supported commands and retrieve their values from the car 
            :returns int: 0 if success, -1 if the list of commands is empty, and -2 if no connection found
        """

        if(self.supported_commands == [] or self.supported_commands == None):
            log.error('No commands to apply!')
            return -1
        elif(self.connection == None):
            log.error('Connection to the car not found!')
            return -2
        else:

            output = []
            output.append('\r\n')
            output.append('-----------------------------------------------\n')
            output.append('Data retrieved on: {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            output.append('-----------------------------------------------\n')

            ## Run commands one by one
            for cmd in self.supported_commands:

                try:                
                    response = self.connection.query(obd.commands[cmd])

                    if(response.is_null()):
                        output.append("[{}] => {}\r\n".format(cmd, 'None'))                        
                    else:
                        output.append("[{}] => {}\r\n".format(cmd, response.value))
                    
                    time.sleep(0.1)
                except Exception as inst:
                    log.error("Exception: {}".format(inst))

            output_str = ''.join(output)
            write_to_file(self.output_file, "a+", output_str)
            return 0

        
