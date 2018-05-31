#!/usr/bin/env python

import time
import control_plug

min2sec = 60
ON_time_sec = 5*min2sec
OFF_time_sec = 2*min2sec

def StartOnOffSequence():
    control_plug.TurnPlugOn()
    time.sleep( ON_time_sec )
    control_plug.TurnPlugOff()
    time.sleep ( OFF_time_sec )


# initial_wait = 2*60*min2sec

# time.sleep(initial_wait)
while True:
    StartOnOffSequence()