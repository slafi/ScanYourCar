# Project Description

The [Onboard Diagnostics Protocol (OBD-II)](https://en.wikipedia.org/wiki/On-board_diagnostics) protocol allows to query the different car engine control units (ECUs) and get real-time data through the CAN bus. The data can be retrieved through specific [parameter identifiers (PIDs)](https://en.wikipedia.org/wiki/OBD-II_PIDs). However, each car supports a subset of the standard PIDs. In addition, some cars use manufacturer-specific PIDs. The ScanYourCar project connects to the car through an OBD reader (e.g., [ELM327](https://en.wikipedia.org/wiki/ELM327)) and checks which PIDs (Mode 2 and Mode 3 only) are supported by that car. It also gets a snapshot of the data for each supported PID.

## Getting Started

To successfully run this source code, a Bluetooth OBD reader is required. It should be paired to your system.

### Prerequisites

This project use the [Python OBD](https://github.com/brendan-w/python-OBD) library. To install this library, you need to run:

```bash
pip install obd
```
On Linux-based systems, you may also need to install the [BlueZ](http://www.bluez.org/about/) stack:

```bash
sudo apt-get install bluetooth bluez-utils blueman
```

### Usage

To run the project from the command line, you just need to issue the following command:

```bash
python3 app.py
```

This code can also be used from another Python script. You need to instantiate and call the `Explorer` class:

```python
## Instantiate the Explorer class
cexplorer = explorer.Explorer(command_file = "./explorer/commands.json", output_file = "./test_result.txt")

## Connect to the car
cexplorer.connect()

## Query the car to get the supported commands
rcode = cexplorer.check_supported_commands()

## Query the car to get current data for each supported command
if rcode == 0:
    cexplorer.run_supported_commands()

## Close connection to the car
cexplorer.disconnect()
```

The `Explorer` class writes supported commands (i.e., PIDs) to the output file `output_file`. In addition, the class member `self.supported_commands` holds the list of supported commands. Before the invocation of the `check_supported_commands()` method, this list is empty.

The `Explorer` class takes as input a list of OBD commands (PIDs) in JSON format. A [default list](examples/commands.json) which enumerates the Mode 2 and 3 commands, supported by Python OBD library, is already provided. If you want to provide your own list of commands, or the [commands' list](https://python-obd.readthedocs.io/en/latest/Command%20Tables/) offered by the library evolves in the future, you still have the option to override the default list (by explicitly setting to `command_file` to your commands' list).

## Examples

The ScanYourCar code retrieved the supported commands from three different cars:
* [Toyota Corolla](examples/output_t.txt) -- Toyota Corolla 2006
* [Hyundai Accent](examples/output_h.txt) -- Hyundai Accent 2007
* [Mazda 3](examples/output_m.txt) -- Mazda 3 2006

## Built With

* [Python 3](https://www.python.org/downloads/)

## Tested on
* [Ubuntu 18.04](http://releases.ubuntu.com/18.04/)
* [Raspian 10](https://www.raspberrypi.org/downloads/raspbian/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for more details.
