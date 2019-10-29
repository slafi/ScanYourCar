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
    
    """ This class checks and logs the PID commands supported by the car 

        :param output_file: the file to which the test results are written
		:param commands: the list of available commands
		:param supported_commands: the list of the commands supported by the car
		:param connection: an OBD-II connection instance
		:param Enabled: a flag indicating whether the class instance is enabled
    """

    def __init__(self, command_file = "./commands.json", output_file = "./output.txt", verbose=False):
		""" Default constructor

            :param command_file: the JSON file from which the predefined list of commands are loaded
			:param output_file: the filename to which the test results are written
			:param verbose: a flag which indicates if thorough debug info are logged
        """
		
        self.output_file = output_file
        self.commands = []
        self.supported_commands = []
        self.connection = None
        self.Enabled = False

        try:
            logger.info(f"Loading standard OBD-II commands from '{command_file}'...")
            with open(command_file) as json_file:  
                data = json.load(json_file)
                
                counter = 0
                for p in data:
                    self.commands.append((p['command'], p['auto-log']))
                    counter += 1
                    if verbose:
                        logger.info(f"{p['command']} -> {p['description']}")
                
                logger.info(f'{counter} OBD-II commands loaded.')
       
        except Exception as inst:
            logger.error(f"Exception: {str(inst)}")


    def connect(self):
        """ Attempts to connect to the ELM327 adapter

            :returns int: 0 if the connection is established, -1 otherwise
        """""" Attempts to connect to the ELM327 adapter

            :returns int: 0 if the connection is established, -1 otherwise
        """
        try:
            self.connection = obd.OBD()
            #self.connection = obd.Async() # auto-connects asynchronously to USB or RF port
            return 0
        except Exception as inst:
            logger.error(f"Exception: {str(inst)}")
            return -1


    def check_connection(self):
        """ Checks if the connection is already established. Returns boolean or None if exception 
            :returns Boolean: True if the connection is already established, False if the connection is not established, None if an exception has occured
        """
        try:

            if(self.connection.status() == obd.OBDStatus.CAR_CONNECTED):
                logger.debug("Explorer is now connected to the car!")
                self.Enabled = True
                return True
            else:
                logger.debug("Explorer could not connect to the car!")
                self.Enabled = False
                return False

        except Exception as inst:
            logger.error(f"Exception: {str(inst)}")
            return None


    def disconnect(self):
        """ Closes the established connection to the ELM327 
            :returns Boolean: True if the connection is closed successfully, False if the connection already not alive/established, None if an exception has occured
        """
        try:

            if(self.connection.status() == obd.OBDStatus.CAR_CONNECTED):
                self.connection.close()
                self.Enabled = True
                logger.debug("Connection to the car is closed!")
                return True
            else:
                logger.debug("Connection to the car is already not alive!")
                return False

        except Exception as inst:
            logger.error(f"Exception: {str(inst)}")
            return None


    def check_supported_commands(self):

        """ Runs through the input list of commands and Checks which among them are suported by the car

            :returns int: 0 if success, -1 if the list of commands is empty, -2 if no connection found, -3 if an exception has occured
        """

        self.supported_commands = []

        try:

            if(self.commands == [] or self.commands is None):
                logger.error('No commands to apply!')
                return -1
            elif(self.connection is None):
                logger.error('Connection to the car not found!')
                return -2
            else:

                output = []
                self.supported_commands=[]
                output.append('-----------------------------------------------\n')
                output.append('\tScanYourCar version 1.0\n')
                output.append(f"\tTest run on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                output.append('-----------------------------------------------\n')
                
                count = 0
                ## Check commands one by one
                for cmd in self.commands:
                    try:
                        is_supported = self.connection.supports(obd.commands[cmd[0]])

                        if is_supported == True:
                            output.append(f"{cmd[0]} .............. [OK]\r\n")
                            self.supported_commands.append(cmd)
                            count += 1
                        else:
                            output.append(f"{cmd[0]} .............. [NOT SUPPORTED]\r\n")

                        time.sleep(0.1)

                    except Exception as inst:
                        logger.error("Exception: {}".format(inst))
                    
                output.append('-----------------------------------------------\n')
                output.append(f'Test results: {count} commands are supported.\n')
                output.append('-----------------------------------------------\n')
                output_str = ''.join(output)
                io.write_to_file(self.output_file, "w", output_str)                    

            return 0

        except Exception as inst:
            logger.error(f"Exception: {str(inst)}")
            return -3


    def run_supported_commands(self):

        """ Attempts to sequentially run supported commands and retrieve their values from the car

            :returns int: 0 if success, -1 if the list of commands is empty, and -2 if no connection found
        """

        if(self.supported_commands == [] or self.supported_commands is None):
            logger.error('No commands to apply!')
            return -1
        elif(self.connection is None):
            logger.error('Connection to the car not found!')
            return -2
        else:

            output = []
            output.append('\r\n')
            output.append('-----------------------------------------------\n')
            output.append(f"Data retrieved on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.append('-----------------------------------------------\n')

            ## Run commands one by one
            for cmd in self.supported_commands:

                try:                
                    response = self.connection.query(obd.commands[cmd[0]])

                    if(response.is_null()):
                        output.append(f"[{cmd[0]}] => None\r\n")                        
                    else:
                        output.append(f"[{cmd[0]}] => {response.value}\r\n")
                    
                    time.sleep(0.1)
                except Exception as inst:
                    logger.error(f"Exception: {str(inst)}")

            output_str = ''.join(output)
            io.write_to_file(self.output_file, "a+", output_str)
            return 0


    def dump_supported_commands(self, dump_file):
    
        """ Dumps the supported PID commands into a JSON file

            :param dump_file: the JSON filename to which the supported commands are written
            :returns int: 0 if success, -1 if the list of commands is empty
        """

        if(self.supported_commands == [] or self.supported_commands is None):
            logger.error('No commands to dump!')
            return -1
        else:

            continuous_logging_commands = []
            onetime_logging_commands = []

            ## Run commands one by one
            for cmd in self.supported_commands:

                try:                
                    if (cmd[1].lower() == "yes"):
                        continuous_logging_commands.append(cmd[0])
                    elif (cmd[1].lower() == "once"):
                        onetime_logging_commands.append(cmd[0])

                except Exception as inst:
                    logger.error(f"Exception: {str(inst)}")

            output = dict()
            output["continuous_logging_commands"] = continuous_logging_commands
            output["onetime_logging_commands"] = onetime_logging_commands

            output_json = json.dumps(output)
            io.write_to_file(dump_file, "w", output_json)
            return 0
            