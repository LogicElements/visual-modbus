# Visual Modbus and Testing Tools

This repository contains visual and testing python application for Modbus RTU slave devices by Logic Elements.


### Supported devices
  - [RTD Emulator](https://logicelements.cz/en/products/rtd-emulator)
  - [Phase Detector](https://logicelements.cz/en/products/power-grid-voltage-detector)
  - [RTD Meter VMS-1502](https://logicelements.cz/en/products/rtd-meter)
	
# Features

The main feature is a graphical application that handles the modbus register map of the device and provides a graphical user interface for working with modbus slave devices. It allows for:
  - Import register map from json file
  - Manage non-standard modbus register composition and decomposition (long integers, float, string)
  - Read and write register operations
  - Update firmware of the device
  
The core modules of VisualModbus can also be used for scripting and testing. Device directories are provided by SimpleVerif*.py script that illustrates how to create a simple script for automated testing. It includes:
  - Read device information
  - Set device parameters
  - Read/write input/output registers
  - Reset device

# Installation

  1. Install python 3.6 or higher
  2. Install dependencies by pip from root of repo

    pip install -r requirements.txt
    
 3. Add path to repo root into python import path, e.g., variable PYTHONPATH
    - For windows, go to "Start" -> "Environmental variables" -> "Add user variable" and add new entry with PYTHONPATH variable containing path to repo, such as "C:\Users\john\my-repos\visual-modbus\\"

# Usage

To run visual modbus for the desired device, go to the device directory and run  Visual*.py script, such as for RTD emulator:

    cd RtdEmulator
    python VisualRtdEmul.py

Such a window should appear.
![Alt text](visual-modbus.png?raw=true "VisualModbus application") 
  - "Settings" -> "Edit" shows window with all settings parameters to change. This can be used to adjust window dimension. First resize window, ge to Edit settings, notice window size has changed, "Save" new settings, close application, rerun application with new size.
  - "Help" shows new window with information.
  - Button "?" shows new window with information of register on the given line.
  - Button "R" reads value of register on the given line only.
  - Label marked as "1" is unique name of the register within the device.
  - Textbox marked as "2" is last read value of the register in native format (decimal, float, string).
  - Textbox marked as "3" is last read value of the register in hexadecimal format if applicable.
  - Label marked as "4" contains minimum and maximum value boundaries of the register.
  - Button "Select file" opens dialog to select file for firmware upgrade.
  - Button "Upgrade" starts the firmware upgrade procedure. Progress window should appear. When finished, progress window should disappear.
  - Textbox marked as "5" shows path to selected firmware file.
  - Button "Write" performs write operation on registers, the value of which has been changed (without pressing "Enter" inside the textbox "2" or "3"). If no register has been changed, the previous write operation is send again. This allows for re-send commands to some trigger register.
  - Button "Write All" writes values of all holding registers.
  - Button "Read" reads all registers.
  - Button "Com open/Com close" opens and closes COM port.
  - Button "Show Log" shows new window containing x most recet log entries.
  - Button "Close" closes the application.
  - Label marked as "6" shows only 1 most recent log entry.

To run simple example script for the desired device, go to the device directory and run SimpleVerif*.py script, such as for RTD emulator:

    cd RtdEmulator
    python SimpleVerifRtdEmul.py

The script only prints the console output messages.

# Settings

There are 3 groups of setting parameters, that can be either set before running VisualModbus in respective json files, or within the application itself. 

### VisualSettings.json
  - "width": 650,   `Window width (approx)`
  - "height": 550,  `Window height (approx)`
  - "slave_address": 1, `Modbus RTU slave address of the device`
  - "reg_map": "Example-FW_Modbus.json", `Json description of device register map`
  - "attempts": 2, `Number of communication attempts`
  - "retry_delay": 0.5,`Delay between communication retries in seconds`
  - "readout_period": 1.0  `Period of a periodic readout in seconds (future use)`
### ComSettings.json
  - "comport": "COM3", `COM port name, for linux may be like /dev/ttyUSB0` 
  - "baud_rate": 19200,  `Communication baud rate`
  - "stop_bits": 1, `Number of stop bits`
  - "parity": "E", `Parity, can be either: "N" - None, "E" - Even, "O" - Odd`
  - "timeout": 1.5,  `Slave response timeout in seconds` 
  - "inter_char_timeout": 30,  `Multiplier of modbus inter-character timeout`
  - "minimal_inter_char_timeout": 0.05, `Minimal inter-character timeout`
  - "silent_interval": 1.0   `Multiplier of silent interval`
### UpgradeSettings.json
  - "align": 4,  `Byte alignment of target MCU memory operations`
  - "page_bytes": 64, `Size of memory page to program at once in bytes`
  - "type_binary": 0,  `Type of binary file (0 - firmware, 1 - graphics or other)`
  - "mode_operation": 1, `Mode of operation (0 - erase-on-the-fly, 1 - erase at start, 2 - apply)`
  - "address": 1000,  `Holding register address used for upgrade`
  - "test_mode": 1, `Test mode (future use)`
  - "init_delay": 0.5, `Initial delay after first packet of upgrade in seconds. Target MCU will erase its memory.`
  - "block_delay": 0.0 `Delay between two pages in seconds`




