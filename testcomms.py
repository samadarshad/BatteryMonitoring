# test connect and send msg to vero ble

from bluetooth import *
import message
import time
import os
import subprocess
import csv
import numpy as np
# import splitHex


MATCH_THRESHOLD = 35
QUALITY_THRESHOLD = 60

env = os.environ.copy()
env["LD_LIBRARY_PATH"] = '/home/pi/SimMatcher'

class Scanner( object ):

    def __init__( self, macAddr ):
        self.macAddr = macAddr
        self.lastReply = None
        self.sock = None

    def connect( self ):
        # connect to Vero
        self.sock=BluetoothSocket( RFCOMM )
        vero = find_service( address = self.macAddr )
        self.sock.connect((vero[0]['host'], 1))

    def disconnect( self ):
        self.sock.close()

    def reconnect(self):
        try: 
            print "reconnecting attempt"
            scanner.connect()
            return True
        except Exception as e:
            print( "reconnection failed - try again.") 
            print( e )
            scanner.disconnect()
            return False

    def sendMsg( self, msg ):
        self.sock.send( msg )
        self.lastReply = message.Message( self.sock.recv( 1024 ) ) #buffer reservation

    def sendMsgUDP( self, msg ):
        self.sock.send( msg )   

    def ok( self ):
        return self.lastReply.status() == 0


def getTemplate( scanner ):
    i = 0
    template = b''
    while True:
        scanner.sendMsg( message.getTemplateFragment( i ))
        if not scanner.ok():
            raise Exception
        template = template + scanner.lastReply.getFragment()
        if scanner.ok() and scanner.lastReply.isLastFragment():
            break
        i = i + 1

    probe = open("probe.fmr", "wb");
    probe.write( template )
    probe.close()

def match(probe, candidate):
    output = subprocess.check_output(['/home/pi/SimMatcher/matcher', probe, candidate], env=env).decode("utf-8").rstrip().split(',')
    return float(output[-1])

def runMatches():
    name = None
    bestScore = 0
    folderName = "./simprinters"
    for file in os.listdir( folderName ):
        if file.endswith(".fmr"):
            candidateName = file
            score = match('./probe.fmr', os.path.join( folderName, file))
            print( score )
            if score > bestScore:
                bestScore = score
                name = candidateName
    return name, bestScore

def sentry():
    scanner = Scanner( macAddr = 'F0:AC:D7:C5:BA:57') # F0:AC:D7:CD:AC:8F' ) # dev board: F0:AC:D7:C5:BA:57
    # 'F0:AC:D7:C0:00:00'
    scanner.connect()

    # wake up UN20
    scanner.sendMsg( message.un20WakeUp )
    time.sleep( 5 )

    door = Door()

    try:
        while True:
            time.sleep( 2 )
            # set resting UI
            scanner.sendMsg( message.restingMsg )
            scanner.sendMsg( message.captureImage )
            if scanner.ok():
                scanner.sendMsg( message.getQuality )
                if not scanner.ok() or scanner.lastReply.getQuality() < QUALITY_THRESHOLD:
                    scanner.sendMsg( message.redSmile )
                    continue

                scanner.sendMsg( message.greenSmile )
                scanner.sendMsg( message.generateTemplate )
                if not scanner.ok():
                    continue
                template = getTemplate( scanner )
                name, bestScore = runMatches()
                print( name )
                print( bestScore )
                if( bestScore > MATCH_THRESHOLD ):
                    scanner.sendMsg( message.accessGrantedLight )
                    door.toggle()
                else:
                    scanner.sendMsg( message.accessDeniedLight )
    except Exception as e:
        print( "cleaning up") 
        print( e )
        scanner.disconnect()
        door.cleanup()



def runScanningIfConnected(scanner):
    try:
        runScanning(scanner)
    except:
        pass

MAX_WAIT_TIME = 25

def runScanning(scanner):

    attempts = 0
    try:        

    # while attempts < MAX_ATTEMPTS:
        waittime = 0
        scanner.sendMsg( message.restingMsg )
        scanner.sendMsg( message.captureImage )
        while (not scanner.ok() and waittime < MAX_WAIT_TIME):
            scanner.sendMsg( message.captureImage )
            time.sleep(0.1)
            waittime = waittime + 1         
        if scanner.ok():
            scanner.sendMsg( message.getQuality ) 
            scanner.sendMsg( message.greenSmile )
            template = getTemplate( scanner )
            # break
        else:
            scanner.sendMsg( message.clearUI )
            # attempts = attempts + 1
            # continue
    except Exception as e:
        # print( "cleaning up") 
        # print( e )
        # scanner.disconnect()
        pass



def getFirmwareVersion(scanner):
    scanner.sendMsg (message.getSensorInfo)
    print "Firmware Version: "
    print(scanner.lastReply.getUcVersion())

def getBatteryIfConnected(scanner):
    try:
        scanner.sendMsg (message.getSensorInfo)    
        return scanner.lastReply.getBattery1Level()
    except:
        try:
            scanner.connect()
            return 0
        except:
            return 0

def getBattery(scanner):
    scanner.sendMsg (message.getSensorInfo)
    return scanner.lastReply.getBattery1Level()

# def getBattery(scanner):
#     scanner.sendMsg (message.getSensorInfo)
#     print "Battery1: "
#     print(scanner.lastReply.getBattery1Level())


protoboard_mac = 'F0:AC:D7:C5:BA:57'
SP657527_mac = 'F0:AC:D7:CA:08:77'
SP568061_mac = 'F0:AC:D7:C8:AA:FD'

# Veros = [
#         ['SP657527', 'F0:AC:D7:CA:08:77'],
#         ['SP568061', 'F0:AC:D7:C8:AA:FD'],
#         ['proto', 'F0:AC:D7:C5:BA:57']
#         ]

Veros = [
        ['SP351543', 'F0:AC:D7:C5:5D:37'],
        ['SP967965', 'F0:AC:D7:CE:C5:1D'],
        ['SP242160', 'F0:AC:D7:C3:B1:F0'],
        ['SP144081', 'F0:AC:D7:C2:32:D1'],
        ['SP246276', 'F0:AC:D7:C3:C2:04'],
        ['SP477471', 'F0:AC:D7:C7:49:1F'],
        ['SP114478', 'F0:AC:D7:C1:BF:2E'],
        ['SP639507', 'F0:AC:D7:C9:C2:13'],
        ['SP872110', 'F0:AC:D7:CD:4E:AE'],
        ['SP359066', 'F0:AC:D7:C5:7A:9A']
        ]

IS_CONTINUOUS_SCANNING = False
# numberOfScanners = len(Veros)
numberOfScanners = 6 # maximum number of BT connected = 7

if __name__ == "__main__":
    scannerlist = []
    data_headers = []
    data_row = []
    data = []
    time_header = "Time"
    time_data = []
    count_header = "Count"
    count_data = []
    
    
    
    for idx in range(0, numberOfScanners):
        scannerlist.append(Scanner(macAddr = Veros[idx][1]))


    for idx in range(0, numberOfScanners):
        scannerlist[idx].connect()
        if (IS_CONTINUOUS_SCANNING):
            scannerlist[idx].sendMsg( message.un20WakeUp )

    

    for idx in range(0, numberOfScanners):
        data_headers.append(Veros[idx][0])


    print(data_headers)

    aggregate_headers = [count_header] + [time_header] + data_headers
    aggregate_data = []

    interval_secs = 2
    total_time_minutes = 10*60
    total_time_secs = total_time_minutes * 60
    maxtime = (int)(total_time_secs / interval_secs)

    # maxtime = 30

    filename = "voltage_measurements_" + time.strftime("%d_%b_%Y_%H%M%S", time.gmtime())
    csvfile = filename + '.csv'
    
    with open(csvfile, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(aggregate_headers)

        for count in range(0, maxtime):
            for idx in range(0, numberOfScanners):
                # data_row.append(getBattery(scannerlist[idx]))
                data_row.append(getBatteryIfConnected(scannerlist[idx]))
                if (IS_CONTINUOUS_SCANNING):
                    runScanningIfConnected(scannerlist[idx])
                time.sleep( interval_secs )
            
            print (data_row)
            data.append(data_row)
            data_row = []
            time_data.append(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
            count_data.append(count)            
            aggregate_data.append([count_data[count]] + [time_data[count]] + data[count])
            writer.writerow(aggregate_data[-1])
            output.flush()
    
    for idx in range(0, numberOfScanners):
        scannerlist[idx].disconnect()

        