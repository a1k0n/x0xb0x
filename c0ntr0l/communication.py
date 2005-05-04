import string
from packet import Packet
from binascii import a2b_hex
from binascii import b2a_hex
from DataFidelity import crc8
from Globals import *

#
# Messages from the c0ntr0l software to the x0xb0x.
#
PING = '01'
WRITE_PATTERN = '02'
READ_PATTERN = '03'
LOAD_PATTERN = '04'
SET_BANK = '05'
GET_BANK = '06'
SET_PATTERN = '07'
GET_PATTERN = '08'
START_SEQUENCER = '09'
STOP_SEQUENCER = '0A'
GET_SEQUENCER_STATE = '0B'
SET_SYNC = '0C'
GET_SYNC = '0D'
SET_TEMPO = '0E'
GET_TEMPO = '0F'

#
# Messages from the x0xb0x to the c0ntr0l software.
#
STATUS = '80'


class DataLink:
    def __init__ (self, serialPort):
        self.s = serialPort

#----------------------- Basic Packet Sending Primitives --------------------

    def sendBasicPacket(self, packetType, content=[]) :        
        header = [packetType]
        
        contentSize = str('%04X' % len(content))
        header.append(contentSize[-2:])
        header.append(contentSize[0:2])

        header = a2b_hex(string.join(header, sep=''))
        content = a2b_hex(string.join(content, sep=''))
        
        packetToSend = header + content + chr(crc8(header + content))
        self.s.write(packetToSend)

    def getBasicPacket(self) :
        self.s.setTimeout(DEFAULT_TIMEOUT)

        packet = Packet([])
        character = self.s.read()
        while character :
            packet.addBytes(character)
            if packet.isComplete :
                break
            character = self.s.read()
        return packet

#----------------- Specific Packet Types ---------------------------------
    def sendPingMessage(self) :
        self.sendBasicPacket(PING)
        packet = self.getBasicPacket()
        if packet.isCorrect:
            packet.printMe()
        else:
            print 'Bad packet!'

    def sendWritePatternMessage(self, pattern) :
        self.sendBasicPacket(WRITE_PATTERN, content = [])
        packet = self.getBasicPacket()
        packet.printMe()

    def sendReadPatternMessage(self) :
        self.sendBasicPacket(READ_PATTERN)
        packet = self.getBasicPacket()
        print packet

    #
    # Sequencer run/stop control
    #
    def sendLoadPatternMessage(self, bank, loc) :
        self.sendBasicPacket(LOAD_PATTERN, content=[a2b_hex(dec2hex(bank)), a2b_hex(dec2hex(loc))])
        packet = self.getBasicPacket()
        print packet

    def sendSetBankMessage(self, bank) :
        self.sendBasicPacket(SET_BANK, content = [a2b_hex(dec2hex(bank))])
        packet = self.getBasicPacket()
        print packet

    def sendGetBankMessage(self) :
        self.sendBasicPacket(GET_BANK)
        packet = self.getBasicPacket()
        print packet

    def sendSetPatternMessage(self, loc) :
        self.sendBasicPacket(SET_PATTERN, content = [a2b_hex(dec2hex(loc))])
        packet = self.getBasicPacket()
        print packet

    def sendGetPatternMessage(self) :
        self.sendBasicPacket(GET_PATTERN)
        packet = self.getBasicPacket()
        print packet

    def sendStartPacket(self) :
        self.sendBasicPacket(START_SEQUENCER)
        packet = self.getBasicPacket()
        print packet

    def sendStopPacket(self) :
        self.sendBasicPacket(STOP_SEQUENCER)
        packet = self.getBasicPacket()
        print packet

    def sendGetSequencerStatePacket(self) :
        self.sendBasicPacket(GET_SEQUENCER_STATE)
        packet = self.getBasicPacket()
        print packet

    #
    # Sync and tempo messages
    #
    def sendSetSyncPacket(self, source) :
        self.sendBasicPacket(SET_SYNC, content = [a2b_hex(source)])
        packet = self.getBasicPacket()
        print packet

    def sendGetSyncPacket(self) :
        self.sendBasicPacket(GET_SYNC)
        packet = self.getBasicPacket()
        print packet

    def sendSetTempoPacket(self, tempo) :
        self.sendBasicPacket(SET_TEMPO, content = [a2b_hex(dec2hex(tempo))])
        packet = self.getBasicPacket()
        print packet

    def sendGetTempoPacket(self) :
        self.sendBasicPacket(GET_TEMPO)
        packet = self.getBasicPacket()
        print packet


        
def dec2hex(dec) :
    hexstring = (hex(dec).upper().split('x'))[1]

    #
    # If necessary, pad the hexstring with a zero so that
    # there are an even number of characters in the string.
    #
    if len(hexstring) % 2 != 0:
        hexstring = '0' + hexstring

    return hexstring
    
