
from Globals import *
import serial
import AvrProgram 
from pattern import Pattern
import IntelHexFormat
from communication import *

import wx
import os
import glob


class Model:

    def __init__(self, controller):
        self.controller = controller
        self.serialconnection = None

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
        if os.name == 'posix':
            self.serialPorts = glob.glob('/dev/cu.*')
        elif os.name == 'nt':
            self.serialPorts = ['COM1', 'COM2', 'COM3', 'COM4']

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
        self.controller.updateSelectedSerialPort(self.currentSerialPort)

        #
        # Finally, open the serial port
        #
        self.openSerialPort()
        
        #
        # Start with an empty active pattern
        #
        self.currentPattern = Pattern('')
        self.controller.updateCurrentPattern(self.currentPattern)

    def destroy(self):
        #
        # Clean up
        #
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
        self.dataLink.sendPingMessage()

    def openSerialPort(self):
        #
        # Attempt to open the serial port.  
        #
        try:
            print 'Trying to open port ' + self.currentSerialPort + ' at ' + str(DEFAULT_BAUD_RATE) + 'bps'

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
            self.serialconnection.close()
            self.controller.updateStatusText('Closed serial port ' + self.currentSerialPort)
            self.controller.updateSerialStatus(False)

    def selectSerialPort(self, name):
        if name in self.serialPorts:
            self.closeSerialPort()
            self.currentSerialPort = str(name)
            self.controller.SetConfigValue('serialport', self.currentSerialPort)
            self.openSerialPort()
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


    def runTest(self):
        self.dataLink.sendPingMessage()

    def readPattern(self, bank, loc):
        try:
            #
            # Note that we subrtract 1 from both the bank and loc here, since the
            # x0xb0x indexes patterns and banks starting at 0 instead of 1.
            #
            patternBytes = self.dataLink.sendReadPatternMessage(bank - 1, loc - 1)
            self.controller.updateCurrentPattern(patternBytes)
        except BadPacketException, e:
            self.controller.updateStatusText('Packet error occured: ' + str(e))

    def writePattern(self, pattern, bank, loc):
        self.dataLink.sendWritePatternMessage(pattern, bank - 1, loc - 1)

    def backupAllPatterns(self, tofile):
        for i in range(1, NUMBER_OF_BANKS):
            for j in range(1, LOCATIONS_PER_BANK):
                pass
    #
    # Meme - these aren't finished yet.
    #
    def restoreAllPatterns(self, fromfile):
        pass

    def sendToggleSequencerMessage(self):
        self.dataLink.sendRunStop()

