# BatteryMonitoring
Script adapted from SimDoor to do battery monitoring


## How to use
- A PC can typically only connect to up to 6 Veros
- Edit the table in testcomms.py to contain the Vero SPxxxxxx and its corresponding Mac address (=hex of xxxxxx)
- All the devices MUST be turned on prior to starting the script
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
