# MQTT Testing Suite

This repository contains a set of scripts designed to test and analyze the performance of an MQTT Mosquitto broker under various conditions. The tests are conducted over 60-second increments and include a variety of configurations to measure message transmission, reception, and ordering.

## Overview

The testing suite conducts 180 tests, each lasting 60 seconds, and varying the following parameters:
- Number of publisher instances (1 to 5)
- Publishing Quality of Service (QoS) levels (0, 1, and 2)
- Delays between published messages (0ms, 1ms, 2ms, and 4ms)

## Libraries Used
- `time`: To keep track of time delays
- `os`: To write to file
- `pandas`: To create dataframes for spreadsheet
- `paho`: For MQTT brokering with the mosquitto broker. 

## Scripts

### `common.py`
Contains global variables used by both publisher and analyser scripts. 
If you need to change either **the broker the scripts connect to** or **the duration of the tests** please modify this file. 

### Publisher Scripts (`pub_1.py` to `pub_5.py`)
- Listen to relevant request topics and publish messages for the set duration
- Log details to `publisher_log.csv`

### Analyser Script (`analyser.py`)
- Captures initial $SYS topics for later calculations
- Publishes relevant request topics and analyses incoming messages
- Logs detailed statistics to `analyser_log.csv`
- Logs system statistics to `sys_log.csv`
- Repeats the process for all 180 tests
- **Please note : The analyser script contains various $SYS topics specific to the Mosquitto broker. If you are planning to run on another broker, these should be modified or removed**

### `run.bat`
- For Windows users: launches all 5 publisher scripts, waits 2 seconds, and then launches the analyser script

## Usage

#### Windows Users
1. Ensure you have administrative privileges.
2. Run the `run.bat` script to start the testing suite.
3. The `run.bat` script will launch all 5 publisher scripts, wait 2 seconds, then launche the analyser script

#### Non-Windows Users
1. Ensure all publisher scripts (`pub_1.py` to `pub_5.py`) are launched before the analyser script (`analyser.py`).
2. Make sure the scripts are run with administrative privileges to allow CSV file creation and writing.

### Modifying Test Parameters
Edit `common.py` to change the MQTT broker or test duration.

## Report
The final report, including the formatted spreadsheet with all 180 test results, provides a comprehensive analysis of the MQTT broker's performance under various conditions. For more detailed analysis and discussion on MQTT statistics, please refer to the accompanying report.

