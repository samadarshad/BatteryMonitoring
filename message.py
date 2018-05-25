
import struct
from enum import Enum, unique
from intelhex import IntelHex

ADDR_SIZE = 6
INT_SIZE = 4
SHORT_SIZE = 2
BYTE_SIZE = 1

MESSAGE_HEADER_BYTES = 0xfafafafa
MESSAGE_FOOTER_BYTES = 0xf5f5f5f5

MESSAGE_OVERHEAD = (INT_SIZE + SHORT_SIZE + BYTE_SIZE + BYTE_SIZE + INT_SIZE)

MESSAGE_LENGTH_OFFSET = INT_SIZE;
MESSAGE_TYPE_OFFSET = (INT_SIZE + SHORT_SIZE);
MESSAGE_STATUS_OFFSET = (INT_SIZE + SHORT_SIZE + BYTE_SIZE);
MESSAGE_CONTENT_OFFSET = (INT_SIZE + SHORT_SIZE + BYTE_SIZE + BYTE_SIZE);

@unique
class LedState(Enum):
    off = 0
    red = 1
    green = 2
    orange = 3
    on = 4

@unique
class MessageType(Enum):
    get_sensor_info = 0
    set_sensor_config = 1
    set_ui = 2
    pair = 3
    report_ui = 4
    capture_image = 5
    capture_progress = 6
    capture_abort = 7
    recover_image = 8
    image_fragment = 9
    store_image = 10
    image_quality = 11
    generate_template = 12
    recover_template = 13
    compare_template = 14
    un20_shutdown = 15
    un20_wakeup = 16
    un20_wakingup = 17
    un20_ready = 18
    un20_isshutdown = 19
    un20_get_info = 20
    get_image_fragment = 21
    get_template_fragment = 22
    un_20_shutdown_no_ack = 23
    get_crash_log = 24
    set_hardware_config = 25
    disable_finger_check = 26
    enable_finger_check = 27    
    connect_to_scanner = 28
    disconnect_from_scanner = 29
    none = 30
    #unknown = 31
    # debug
    iap_init = 33
    read_flash = 34   
    set_hex_numbered_packet = 37
    set_flashing_metadata = 38
    get_running_bank_id = 39
    set_running_bank_id = 40
    unknown = 41 # this needs to be updated every time a new message type is added

# encoding outbound messages
def setHeader( msgType, payloadLen = 0):
    return struct.pack('<IHBB', MESSAGE_HEADER_BYTES, payloadLen + MESSAGE_OVERHEAD, msgType, 0 ) # <IHBB = little-endian (ordering of bits upon sending), Integer (4byte), short Integer (2 byte), bit (1byte), bit(1byte)
# so total header = 8 bytes = 16 hex digits    
def setFooter():
    return struct.pack('<I', MESSAGE_FOOTER_BYTES)

def uiPayload( leds ):
    return struct.pack('<8B', 1, 1, 0, *leds) + struct.pack('<H', 0)
    # 8integer: 1 1 0 0 0 3 0 0 0
# boEnableTrigg ^
# boSetLeds;      ^
# boTriggerVibrate  ^
# bLedState           ^ ^ ^ ^ ^
# iVibrateMs;                   ^

def templateFragmentPayload( fragmentNum ):
    return struct.pack('<H', fragmentNum)

def createMessage( msgType, payload = b''):
    return setHeader(msgType=msgType, payloadLen = len(payload))  + payload + setFooter()

def getTemplateFragment( num ):
    return createMessage( MessageType.get_template_fragment.value, templateFragmentPayload( num ))

PACKET_SIZE = '100'
def stringPayload( char ):
    return struct.pack('<' + PACKET_SIZE + 's', char) #testing char initially - later moving to string, then later moving to .bin file. I need to make this 100 bytes long to be in sync with the device. 

def hexFilePayloadtoHumanReadableforDebugging ( filename, format = 'hex' ):
    ih = IntelHex()
    ih.fromfile( filename, format)
    ih.dump()

HEX_PACKET_SIZE = '512' #1012
def hexFilePayload( filename ):
    data = open( filename, 'r').read()
    return struct.pack('<' + HEX_PACKET_SIZE + 's', data) #try 's' string format first, then try int later



def hexFileNumberedPayload( filename, packetNumber, totalPackets, packetSize = 512):
    data = open( filename, 'r').read()
    return struct.pack('<III' + HEX_PACKET_SIZE + 's', packetNumber, totalPackets, packetSize, data) # package number (int), total number of packages (int), size of payload (bytes), payload.

def hexFileNumberedPayload_dataonly_debugging( filename ):
    data = open( filename, 'r').read()
    return struct.pack('<' + HEX_PACKET_SIZE + 's', data) # package number (int), total number of packages (int), size of payload (bytes), payload.
       

# def recordData ( filename ):
    #pack record data
# def metadataOfImage ( flashsizeBytes, startAddr, noOfPackets, CRCofbinary):
#     return struct.pack('<IIIH', flashsizeBytes, startAddr, noOfPackets, CRCofbinary)
def metadataOfImage ( flashsizeBytes, startAddr, CRCofbinary):
    return struct.pack('<IIH', flashsizeBytes, startAddr, CRCofbinary)
    
def numberedHexPacket (number, data):   
    payload = struct.pack("<II" + str(len(data)) + 's', number, len(data), data)
   # payload = struct.pack("<" + str(len(data)) + 's', data)
    return payload

FIXED_PACKET_DATA_SIZE = 800 # must be >= 704 bytes (which is the ihex bytes for 256 binary bytes)
def numberedHexPacketWithPadBytes (number, data):
    noOfDataBytes = len(data)
    noOfPadBytes = FIXED_PACKET_DATA_SIZE-noOfDataBytes
    assert(noOfPadBytes >= 0)
    payload = struct.pack("<II" + str(noOfDataBytes) + 's' + str(noOfPadBytes) + 'x', number, noOfDataBytes, data)
   # payload = struct.pack("<" + str(len(data)) + 's', data)
    return payload

def setBankID ( bankID, resetNVIC):
    return struct.pack('<BB', bankID, resetNVIC)

# decoding inbound messages
class Message( object ):
    
    @staticmethod
    def _decodeType( byteString ):
        value = struct.unpack_from( 'B', byteString, MESSAGE_TYPE_OFFSET)[0] & 0x7f
        if value > MessageType.unknown.value:
            return MessageType.unknown
        else:
            return MessageType( value )

    def __init__( self, byteString ): # this is called for every message input - it takes the header, footer and other metadata. The below functions then deals with the payload spceifically. I need to create a payload decoder for the 'get_sensor_info' message type.
        header = struct.pack('<I', MESSAGE_HEADER_BYTES )
        footer = setFooter()
        if (len(byteString) < len(header) + len(footer)) or byteString[:len(header)] != header or byteString[-len(footer):] != footer:
            raise Exception
        self.byteString = byteString
        self.msgType = Message._decodeType( byteString )

    def status( self ):
        return struct.unpack_from( 'B', self.byteString, MESSAGE_STATUS_OFFSET)[0]
    
    def getType( self ):
        return self.msgType

    def getUcVersion( self ):
        if self.msgType != MessageType.get_sensor_info:
            raise Exception
        return struct.unpack_from( 'H', self.byteString, MESSAGE_CONTENT_OFFSET + ADDR_SIZE)[0]
        #NO_COMMIT    

    def getBattery1Level( self ):
        if self.msgType != MessageType.get_sensor_info:
            raise Exception
        return struct.unpack_from( 'H', self.byteString, MESSAGE_CONTENT_OFFSET + ADDR_SIZE + 2*SHORT_SIZE)[0]
        #NO_COMMIT 

    def getBankID( self ):
        if self.msgType != MessageType.get_running_bank_id:
            raise Exception
        return struct.unpack_from( 'b', self.byteString, MESSAGE_CONTENT_OFFSET)[0]
    
    def getQuality( self ):
        if self.msgType != MessageType.image_quality: 
            raise Exception
        return struct.unpack_from( 'H', self.byteString, MESSAGE_CONTENT_OFFSET)[0]

    def getFragmentNumber( self ):
        if self.msgType != MessageType.get_template_fragment: 
            raise Exception 
        return struct.unpack_from( 'H', self.byteString, MESSAGE_CONTENT_OFFSET)[0]

    def isLastFragment( self ):
        if self.msgType != MessageType.get_template_fragment: 
            raise Exception 
        return struct.unpack_from( 'B', self.byteString, MESSAGE_CONTENT_OFFSET + 2*SHORT_SIZE)[0] != 0

    def getFragment( self ):
        if self.msgType != MessageType.get_template_fragment: 
            raise Exception 
        length = struct.unpack_from( 'B', self.byteString, MESSAGE_CONTENT_OFFSET + SHORT_SIZE)[0]
        start = MESSAGE_CONTENT_OFFSET + 2*SHORT_SIZE + BYTE_SIZE
        return self.byteString[ start:start+length]
        
        

# useful outbound messages
clearUI = createMessage( MessageType.set_ui.value, 
                            uiPayload([LedState.off.value, LedState.off.value, LedState.off.value, LedState.off.value, LedState.off.value]))
restingMsg = createMessage( MessageType.set_ui.value, 
                            uiPayload([LedState.off.value, LedState.off.value, LedState.orange.value, LedState.off.value, LedState.off.value]))
greenSmile = createMessage( MessageType.set_ui.value, 
                            uiPayload([LedState.green.value, LedState.green.value, LedState.green.value, LedState.green.value, LedState.green.value]))
redSmile = createMessage( MessageType.set_ui.value, 
                            uiPayload([LedState.red.value, LedState.red.value, LedState.red.value, LedState.red.value, LedState.red.value]))
accessGrantedLight = createMessage( MessageType.set_ui.value, 
                            uiPayload([LedState.green.value, LedState.off.value, LedState.off.value, LedState.off.value, LedState.green.value]))
accessDeniedLight = createMessage( MessageType.set_ui.value, 
                            uiPayload([LedState.red.value, LedState.off.value, LedState.off.value, LedState.off.value, LedState.red.value]))
                            
captureImage = createMessage( MessageType.capture_image.value )
getQuality = createMessage( MessageType.image_quality.value )
generateTemplate = createMessage( MessageType.generate_template.value )
un20WakeUp = createMessage( MessageType.un20_wakeup.value )
# un20Shutdown = createMessage( MessageType.un20_shutdown.value )

getSensorInfo = createMessage( MessageType.get_sensor_info.value)

def setRunningBankID(bankID, resetNVIC):
    return createMessage ( MessageType.set_running_bank_id.value, setBankID(bankID, resetNVIC))


getRunningBankID = createMessage( MessageType.get_running_bank_id.value)

if __name__ == '__main__':
    expected = {
    'un20WakeUp': b'\xfa\xfa\xfa\xfa\x0c\x00\x10\x00\xf5\xf5\xf5\xf5',
    'getScannerInfo': b'\xfa\xfa\xfa\xfa\x0c\x00\x00\x00\xf5\xf5\xf5\xf5',
    'captureImage':b'\xfa\xfa\xfa\xfa\x0c\x00\x05\x00\xf5\xf5\xf5\xf5',
    'getQuality':b'\xfa\xfa\xfa\xfa\x0c\x00\x0b\x00\xf5\xf5\xf5\xf5',
    'generateTemplate':b'\xfa\xfa\xfa\xfa\x0c\x00\x0c\x00\xf5\xf5\xf5\xf5',
    'getFragmentZero':b'\xfa\xfa\xfa\xfa\x0e\x00\x16\x00\x00\x00\xf5\xf5\xf5\xf5'
    }

   
    # print ":".join("{:02x}".format(ord(c)) for c in setMetadataOfImage)