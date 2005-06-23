# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import string
from binascii import a2b_hex
from binascii import b2a_hex
from DataFidelity import *

PACKET_HEADER_SIZE = 3

class Packet :
    
    def __init__(self, packetList=[]) :
        self.packetList = packetList
        self.extractPacketFromHexList()

    def extractPacketFromHexList(self) :
        self.isComplete = False
        self.isCorrect = False
        self.packetType = None
        self.contentSize = None
        self.CRC = None
        self.headerList = []
        self.contentList = []
        self.actualCRC = None
        for i in range(len(self.packetList)) :
            if i == 0 :
                self.packetType = self.packetList[i].upper()
            elif i == 1 :
                self.contentSize = self.packetList[i].upper()
            elif i == 2 :
                self.contentSize = self.contentSize + self.packetList[i].upper() 
            elif i == 3 :
                self.headerList = self.packetList[:PACKET_HEADER_SIZE]
                self.contentList = self.packetList[PACKET_HEADER_SIZE:]
                if (int(self.contentSize, 16) + 1) == len(self.contentList):
                    
                    # Grab the CRC out of the very last byte in the packet
                    self.CRC = self.contentList[-1]

                    # Grab the remaining content bytes.
                    self.contentList = self.contentList[:int(self.contentSize,16)]
                    self.isComplete = True

                    self.actualCRC = str('%02X' % ord(crc8(a2b_hex(string.join(self.headerList + self.contentList, sep = '')))))

                    #
                    # Meme : For CRC Debugging...
                    #
                    #                    print self.packetList
                    #                    print string.join(self.headerList + self.contentList, sep = '')
                    #                    print ord(crc8(a2b_hex(string.join(self.headerList + self.contentList, sep = ''))))
                    #                    print 'Actual CRC: ' + self.actualCRC
                    
                    if (self.CRC == self.actualCRC) :
                        self.isCorrect = True
    
    def addBytes(self, byteString) :
        # Expects a string of ASCII data.
        if self.isComplete or not byteString :
            return
        for i in range(len(byteString)) :
#            print 'Appending byte: ' + b2a_hex(byteString[i]).upper()
            self.packetList.append(b2a_hex(byteString[i]).upper())
            if len(self.packetList) >= PACKET_HEADER_SIZE :
                self.extractPacketFromHexList()
                if self.isComplete :
                    # This packet is complete, give the remaining bytes back.
                    return byteString[i+1:]
        return ''
            



    def printMe(self) :
        if self.headerList :
            print '\n================================ Start Packet ============='
            print '     packetType: ' + self.packetType 
            print '    contentSize: ' + self.contentSize
            if self.CRC == self.actualCRC :
                print '      CRC: ' + str(self.CRC) + '    ( PASSED: ' + str(self.isCorrect) + ' )'
            else :
                print '      CRC: ' + self.CRC + ' FAILED.  Computed CRC: ' + self.actualCRC
            print '        content: ' + str(self.contentList)
            print '================================ End Packet ===============\n'
        else :
            print '*** INCOMPLETE PACKET ***'
            print '* received ' + str(len(self.contentList)) + ' bytes:'
            print '* ' + str(self.packetList[:PACKET_HEADER_SIZE])

    def messageType(self):
        return a2b_hex(self.packetList[0])

    def content(self):
        return a2b_hex(string.join(self.contentList, sep = ''))

    def size(self):
        return a2b_hex(self.packetList[1:2])
