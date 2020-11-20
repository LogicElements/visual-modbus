# Visual Modbus and Testing Tools

This repository contains visual and testing python application for Modbus RTU slave devices by Logic Elements.


### Supported devices
  - [RTD Emulator](https://logicelements.cz/en/produkty/rtd-emulator)
  - Phase Detector
  - RTD Meter VMS-1502
	
# Features

The main feature is a graphical application that handles the modbus register map of the device and provides a graphical user interface for working with modbus slave devices.

![Alt text](visual-modbus.png?raw=true "VisualModbus application") 

# Installation

  1. Install python 3.6 or higher
  2. Install dependencies by pip from root of repo

    pip install -r requirements.txt
    
 3. Add path to repo root into python import path, e.g., variable PYTHONPATH
    - For windows, go to "Start" -> "Environmental variables" -> "Add user variable" and add new entry with PYTHONPATH variable containing path to repo, such as "C:\Users\john\my-repos\visual-modbus\\"

# Usage

To run visual modbus for given supported device, go to the device directory and run  VisualXxxx.py script, such as for RTD emulator:

    cd RtdEmulator
    python VisualRtdEmul.py
    
# Settings

There are 3 groups of setting parameters, that can be either set before running VisualModbus in respective json files, or within the application itself. 

### VisualSettings.json
  - "width": 650,   `Window width (approx)`
  - "height": 550,  `Widnow height (approx)`
  - "slave_address": 1, `Modbus RTU slave address of the device`
  - "reg_map": "Example-FW_Modbus.json", `Json description of device register map`
  - "attempts": 2, `Number of communication attempts`
  - "retry_delay": 0.5,`Delay between communication retries in seconds`
  - "readout_period": 1.0  `Period of aperiodic readout in seconds (future use)`
### ComSettings.json
  - "comport": "COM3", `COM port name, for linux may be like /dev/ttyUSB0` 
  - "baud_rate": 19200,  `Communication baud rate`
  - "stop_bits": 1, `Number of stop bits`
  - "parity": "N", `Parity, can be either: "N" - None, "E" - Even, "O" - Odd`
  - "timeout": 1.5,  `Slave response timeout in seconds` 
  - "inter_char_timeout": 30,  `Multiplier of modbus inter-character timeout`
  - "minimal_inter_char_timeout": 0.05, `Minimal inter-character timeout`
  - "silent_interval": 1.0   `Multiplier of silent interval`
  - 
### UpgradeSettings.json
  - "align": 4,  `Byte alignment of target MCU memory operations`
  - "page_bytes": 64, `Size of memory page to program at once in bytes`
  - "type_binary": 0,  `Type of binary file (0 - firmware, 1 - graphics or other)`
  - "mode_operation": 1, `Mode of operation (0 - erase-on-the-fly, 1 - erase at start, 2 - apply)`
  - "address": 1000,  `Holding register address used for upgrade`
  - "test_mode": 1, `Test mode (future use)`
  - "init_delay": 0.5, `Initial delay after first packet of upgrade in seconds. Target MCU will erase its memory.`
  - "block_delay": 0.0 `Delay between two pages in seconds`




