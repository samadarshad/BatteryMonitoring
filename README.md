# BatteryMonitoring
Script adapted from SimDoor to do battery monitoring


## How to use
- Pair the PC with all Veros that will be tested
- Edit the table in testcomms.py to contain the Vero SPxxxxxx and its corresponding Mac address (=hex of xxxxxx)

- run 
> python log_voltages.py
- this will start collecting data: display it on output and save it to file with filename like voltage_measurements_23_May_2018_183222.csv
- you may stop the process at any time, or disconnect or turn off any vero after script has begun. Any disconnected Vero it will automatically try to reconnect peroidically.

## Prereq
- note you may need to install prerequisites:
> pip install pybluez

and other prerequisites that you need to run the script.

## Options
- you can get the Veros to take finger print scans by setting
> IS_CONTINUOUS_SCANNING = True

- if you have a TP-Link Wifi Power Socket, and wish to monitor the charging over time (by having the Veros charge for 5 minutes, then unplug for 2 minutes to do measuring, then repeat), you can run another process:
> python charging_sequence.py

Note you may need to find the IP address of the Wifi Power hub (through Angry IP, scanning 192.168.86.0 - 192.168.86.255, looking for 'tp-link hub') and edit the IP address in control_plug.py
