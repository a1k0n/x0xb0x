
from Globals import *
import serial
import AvrProgram 
from pattern import Pattern
import IntelHexFormat
from communication import *

class Model:

    def __init__(self, controller):
        self.controller = controller

        #
        # Attempt to open the serial port
        #
        

    def __del__(self):
        #
        # Clean up
        #
        self.serialconnection.close()

    #
    # This function is called once the model, view, and controller have
    # all been connected in main.py.  This is where most of the
    # initialization code is carried out.
    #
    def initialize(self):
        #
        # Attempt to open the serial port.
        #
        try:
            print 'Trying to open port ' + DEFAULT_COMM_PORT + ' at ' + str(DEFAULT_BAUD_RATE) + 'bps'
            self.serialconnection = serial.Serial(DEFAULT_COMM_PORT, DEFAULT_BAUD_RATE)
            self.dataLink = DataLink(self.serialconnection)
            self.controller.updateStatusText('Opened serial port ' + self.serialconnection.portstr + ' at ' + str(DEFAULT_BAUD_RATE) + ' baud.')
        except serial.SerialException, sce:
            self.controller.updateStatusText('Couldn\'t open serial port!')
            print 'Couldn\'t open.'
            return None


        #
        # Start with an empty active pattern
        #
        self.currentPattern = Pattern('')
        self.controller.updateCurrentPattern(self.currentPattern)


    #
    # Parse a IHX file and upload it to the bootloader.
    #
    def uploadHexfile(self, filename):
        #
        # Meme - Add some robust error handling here.
        #
        ihx = IntelHexFormat.IntelHexFile(filename)
        if self.serialconnection and (AvrProgram.findAVRBoard(self.serialconnection) == True):

            controller.updateStatusText('Uploading firmware....')

            try:
                AvrProgram.doFlashProgramming(self.serialconnection, ihx.toByteString())
                
            except serial.SerialException, e:
                controller.updateStatusText('Programming failed: ' + e.value)

            controller.updateStatusText('Firmware Upload Complete.')

    def runTest(self):
        self.dataLink.sendPingMessage()
