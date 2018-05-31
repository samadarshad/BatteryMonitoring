#!/usr/bin/env python

# import time
import subprocess

# use AngryIP scanner to find the IP of the plug
IPAddrOfPlug = '192.168.86.98'

dirTpLink = "C:\Users\Samad Arshad\Documents\GitHub\\tplink-smartplug\\tplink-smartplug.py"

def CallTPSubprocess(command):
    subprocess.call(['python', dirTpLink, '-t', IPAddrOfPlug, '-c', command])

def TurnPlugOn():
    CallTPSubprocess('on')

def TurnPlugOff():
    CallTPSubprocess('off')

def GetPlugInfo():
    CallTPSubprocess('info')

# subprocess.call(['dir'], shell=True)

# TurnPlugOn()
# time.sleep( 4 )
# TurnPlugOff()