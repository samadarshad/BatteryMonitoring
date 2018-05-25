# BatteryMonitoring
Script adapted from SimDoor to do battery monitoring


How to use:

- A PC can typically only connect to up to 6 Veros
- Edit the table in testcomms.py to contain the Vero SPxxxxxx and its corresponding Mac address (=hex of xxxxxx)
- All the devices must be turned on prior to starting the script
- run 
> python testcomms.py
- this will start collecting data


- note you may need to install prerequisites:
> pip install pybluez
and other prerequisites that you need to run the script.
