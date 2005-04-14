

import serial
from AvrProgram import *
import IntelHexFormat

class Model:

    def __init__(self, controller):
        self.controller = controller

    def testport(self):

        portname = '/dev/cu.usbserial-3B1'
#        portname = '/dev/cu.modem'
        baudrate = 19200
        
        try:
            print 'Trying to open port ' + portname + ' at ' + str(baudrate) + 'bps'
            serialconnection = serial.Serial(portname, baudrate)
        except serial.SerialException, sce:
            print 'Couldn\'t open.'
            return false
        
        pathtohexfile = '/Users/mbroxton/Documents/Projects and Interests/x0xb0x/firmware/x0xb0x.hex'
        ihx = IntelHexFormat.IntelHexFile(pathtohexfile)
        if findAVRBoard(serialconnection) == True:
            print "Programming!"
            try:
                doFlashProgramming(serialconnection, ihx.toByteString())
            except serial.SerialException, e:
                print 'Programming failed: ' + e.value

            

        serialconnection.close()
        


    
