
from Globals import *
import serial
import AvrProgram 
from pattern import Pattern
import IntelHexFormat
import PatternFile
from communication import *
import time
from threading import *
from binascii import a2b_hex

import wx
import os
import glob

class Model:
            
    def __init__(self, controller):
        self.controller = controller
        self.serialconnection = None
        self.worker = None

    #
    # This function is called once the model, view, and controller have
    # all been connected in main.py.  This is where most of the
    # initialization code is carried out.
    #
    def initialize(self):

        #
        # We first have to discover the names of the serial ports.  The method for
        # doing this varies slightly from platform to platform.
        #
        # Meme - Linux support has not yet been implemented here.
        #
	print "OS is "+os.name
        if os.name == 'posix':
            self.serialPorts = glob.glob('/dev/cu.*') + glob.glob('/dev/tts/ttyUSB*') + glob.glob('/dev/ttyUSB*')
        elif os.name == 'nt':
            self.serialPorts = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10']

        print "Found the following serial ports: "+str(self.serialPorts)


        #
        # Check to make sure there are valid serial ports.  If not, quit
        # with an error message.
        #
        if len(self.serialPorts) == 0:
            self.controller.displayModalStatusError('Error: The c0ntr0l application could not find any suitable serial ports.  Please check to make sure that you have one installed.')
            self.controller.quitApp()
        else:
            self.currentSerialPort = str(self.controller.GetConfigValue('serialport'))
            if self.currentSerialPort == "":
                #
                # No serial port found in the preference file.  Use the first
                # port in the list.
                #
                self.currentSerialPort = self.serialPorts[0]

        #
        # Update the menu names in the GUI to reflect the serial port
        # names and the name of the current selection.
        #
        self.controller.updateSerialPortNames(self.serialPorts)
        if self.currentSerialPort in self.serialPorts:
            #
            # Finally, open the serial port
            #
            self.controller.updateSelectedSerialPort(self.currentSerialPort)
        else:
            self.controller.updateStatusText("Error: Previously selected serial port not available.  Please select a new port.")
            self.controller.updateSerialStatus(False);
                
        #
        # Start with an empty active pattern
        #
        self.currentPattern = Pattern('')
        self.controller.updateCurrentPattern(self.currentPattern)

    def destroy(self):
        #
        # Clean up
        #
        self.controller = None
        self.closeSerialPort()

        
    ##
    #
    # VIEW --> MODEL INTERFACE definitions
    #
    ######################################

    #
    # Meme - for debugging.
    #
    def runTest(self):
        self.commlock = True
        val = self.dataLink.sendPingMessage()
        self.commlock = False
        return val
    
    def openSerialPort(self):
        #
        # Attempt to open the serial port.  
        #
        try:
            self.controller.updateStatusText('Trying to open port ' + self.currentSerialPort + ' at ' + str(DEFAULT_BAUD_RATE) + 'bps')

            self.serialconnection = serial.Serial(self.currentSerialPort, DEFAULT_BAUD_RATE)
            self.dataLink = DataLink(self.serialconnection)

            #
            # Update the displayed state in the GUI
            #
            self.controller.updateStatusText('Opened serial port ' + self.serialconnection.portstr + ' at ' + str(DEFAULT_BAUD_RATE) + ' baud.')
            self.controller.updateSerialStatus(True)
            return True

        except serial.SerialException, sce:
            print 'Error: Unable to open serial port ' + self.currentSerialPort + ' at ' + str(DEFAULT_BAUD_RATE) + 'bps'
            serialconnection = None

            self.controller.updateStatusText('Error: Unable to open serial port ' + self.currentSerialPort + ' at ' + str(DEFAULT_BAUD_RATE) + 'bps')
            self.controller.updateSerialStatus(False)
            return False

    def closeSerialPort(self):
        if self.serialconnection:
            if self.worker:
                self.worker.abort()
                self.worker = None
            time.sleep(1);
            self.serialconnection.close()
            #
            # A slight special case.  If the program is closing, the GUI is already
            # gone so we cannot update any longer.  Checx to see if the controller
            # exists, for if it does, the GUI can be written to.
            #
            if self.controller:
                self.controller.updateStatusText('Closed serial port ' + self.currentSerialPort)
                self.controller.updateSerialStatus(False)

    def connectSerialPort(self):
        if self.serialconnection:
            if self.worker:
                self.worker.abort()
                self.worker = None
            self.worker = WorkerThread(self)
                                       
    def selectSerialPort(self, name):
        if name in self.serialPorts:
            self.currentSerialPort = str(name)
            self.controller.SetConfigValue('serialport', self.currentSerialPort)
            self.controller.updateStatusText('')
            return True
        else:
            print 'Error: Cannot select the serial port named ' + name
            return False

    #
    # Parse a IHX file and upload it to the bootloader.
    #
    def uploadHexfile(self, filename):
        #
        # Meme - Add some robust error handling here.
        #
        ihx = IntelHexFormat.IntelHexFile(filename)
        if self.serialconnection and (AvrProgram.findAVRBoard(self.serialconnection) == True):

            self.controller.updateStatusText('Uploading firmware....')
            try:
                AvrProgram.doFlashProgramming(self.serialconnection, ihx.toByteString())
                
            except serial.SerialException, e:
                self.controller.updateStatusText('Programming failed: ' + e.value)

            self.controller.updateStatusText('Firmware Upload Complete.')


    def readPattern(self, bank, loc):
        try:
            #
            # Note that we subrtract 1 from both the bank and loc here, since the
            # x0xb0x indexes patterns and banks starting at 0 instead of 1.
            #
            self.commlock = True
            pattern = self.dataLink.sendReadPatternMessage(bank - 1, loc - 1)
            self.commlock = False
            self.controller.updateCurrentPattern(pattern)
            self.controller.updateStatusText('Pattern loaded from bank: ' + str(bank) + ' loc: ' + str(loc))
            return True
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))
            self.commlock = False
            return False
        except AttributeError, e:
            self.controller.updateStatusText('Error: Not connected.  Please choose a serial port from the Serial menu.')
            self.commlock = False
            return False

    def writePattern(self, pattern, bank, loc):
        try:
            #
            # Note that we subrtract 1 from both the bank and loc here, since the
            # x0xb0x indexes patterns and banks starting at 0 instead of 1.
            #
            self.commlock = True
            self.dataLink.sendWritePatternMessage(pattern, bank - 1, loc - 1)
            self.commlock = False
            self.controller.updateStatusText('Pattern written to bank: ' + str(bank) + ' loc: ' + str(loc))
            return True
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))
            self.commlock = False
            return False
        except AttributeError, e:
            self.commlock = False
            self.controller.updateStatusText('Error: No serial port available.  Please choose a serial port from the Serial menu.')
            return False

    # Send a pattern to the x0x and have it loop it up!
    def playPattern(self, pattern):
        try:
            self.commlock = True
            self.dataLink.sendPlayPatternMessage(pattern)
            self.commlock = False
            self.controller.updateStatusText('Playing pattern')
            return True
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))
            self.commlock = False
            return False
        except AttributeError, e:
            self.controller.updateStatusText('Error: No serial port available.  Please choose a serial port from the Serial menu.')
            self.commlock = False
            return False

    def stopPattern(self, pattern):
        try:
            self.commlock = True
            self.dataLink.sendStopPatternMessage()
            self.commlock = False
            self.controller.updateStatusText('Stopped playing pattern')
            return True
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))
            self.commlock = False
            return False
        except AttributeError, e:
            self.controller.updateStatusText('Error: No serial port available.  Please choose a serial port from the Serial menu.')
            self.commlock = False
            return False
    
    def backupAllPatterns(self, toFile):
        pf = PatternFile.PatternFile()
        try:
            for bank in range(1, NUMBER_OF_BANKS):
                for loc in range(1, LOCATIONS_PER_BANK):
                    self.commlock = True
                    pattern = self.dataLink.sendReadPatternMessage(bank - 1, loc - 1)
                    pf.appendPattern(pattern, bank, loc)
            pf.writeFile(toFile)
            self.controller.updateStatusText('EEPROM download was succesful.')
        except BadPacketException, e:
            self.controller.displayModalStatusError('An unexpected communication error occured while downloading patterns.  Pattern file was not saved.')
        except AttribuetError, e:
            self.controller.displayModalStatusError('No serial port connected.  Please select a serial port and try again.')
        except IOError, e:
            self.controller.displayModalStatusError('Error writing x0xb0x pattern file.')
        except PatternFileException, e:
            self.controller.displayModalStatusError('Error writing x0xb0x pattern file.')
        self.commlock = False

    def restoreAllPatterns(self, fromFile):
        pf = PatternFile.PatternFile()
        try:
            pf.readFile(fromFile)
            for i in range(pf.numEntries()):
                [bank, loc, pattern] = pf.getNextPattern()
                self.commlock = True
                self.dataLink.sendWritePatternMessage(pattern, bank - 1, loc - 1)
            self.controller.updateStatusText('EEPROM upload was succesful.')
        except BadPacketException, e:
            self.controller.displayModalStatusError('An unexpected communication error occured while downloading patterns.  Pattern file was not saved.')
        except AttributeError, e:
            self.controller.displayModalStatusError('No serial port connected.  Please select a serial port and try again.')
        except IOError, e:
            self.controller.displayModalStatusError('Error reading x0xb0x pattern file.')
        except PatternFileException, e:
            self.controller.displayModalStatusError('Error reading x0xb0x pattern file.')
        self.commlock = False
                            
    def eraseAllPatterns(self):
        try:
            for bank in range(1, NUMBER_OF_BANKS):
                for loc in range(1, LOCATIONS_PER_BANK):
                    self.commlock = True
                    self.dataLink.sendWritePatternMessage(Pattern(), bank - 1, loc - 1)
            self.controller.updateStatusText('EEPROM successfully erased.')
        except BadPacketException, e:
            self.controller.displayModalStatusError('An unexpected communication error occured while downloading patterns.  Pattern file was not saved.')
        except AttributeError, e:
            self.controller.displayModalStatusError('No serial port connected.  Please select a serial port and try again.')
        self.commlock = False

    def sendToggleSequencerMessage(self):
        self.commlock = True
        self.dataLink.sendRunStop()
        self.commlock = False

    def readTempo(self):
        self.commlock = True;
        try:
            tempo = self.dataLink.sendGetTempoPacket()
            self.commlock = False
            self.controller.updateTempo(tempo)
            return True
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))
            self.commlock = False
            return False
        except AttributeError, e:
            self.controller.updateStatusText('Error: Not connected.  Please choose a serial port from the Serial menu.')
            self.commlock = False
            return False
        
    def setTempo(self,tempo):
        #print "setting tempo"
        self.commlock = True
        try:
            self.dataLink.sendSetTempoPacket(tempo)
            self.commlock = False
            return True
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))
            self.commlock = False
            return False
        except AttributeError, e:
            self.controller.updateStatusText('Error: Not connected.  Please choose a serial port from the Serial menu.')
            self.commlock = False
            return False
        
    def serialPortBusy(self):
        return self.commlock
    
    def packetWaiting(self):
        return self.dataLink.packetWaiting()

    def processPushedPacket(self):
        packet = self.dataLink.getPushedPacket()
        if (packet == None):
            return
        #print 'got packet '+str(packet.messageType())
        #packet.printMe()
        if (packet.messageType() == TEMPO_MSG):
            tempo = (ord(a2b_hex(packet.contentList[0]))<< 8) + ord(a2b_hex(packet.contentList[1]))
            #print 'tempo = '+str(tempo)
            self.controller.updateTempo(tempo)
        
class WorkerThread(Thread):
    def __init__(self, model):
        Thread.__init__(self)
        self._model = model
        self._want_abort = 0
        print 'thread start\n'
        self.start()

    def run(self):
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        while True:
            if (not self._model.serialPortBusy()):
                #print '.'
                v = self._model.packetWaiting()
                if (v != 0):
                    #print '!'+str(v)
                    self._model.processPushedPacket()
            else:
                time.sleep(.3)
                
            if self._want_abort:
                #wxPostEvent(self._notify_window,ResultEvent(None))
                return


    def abort(self):
        # Method for use by main thread to signal an abort
        self._want_abort = 1
