#
# Copyright (c) 2002-2004. All rights reserved.
#
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

#----------------------------------------------------------------------------
# Name:         PatternFile.py
# Purpose:      A class for reading and writing x0xb0x pattern files.
#               The pattern file format is documented in docs/file_formats.txt.
#
# Author:       Michael Broxton
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2005
#----------------------------------------------------------------------------

from Globals import *
from binascii import a2b_hex, b2a_hex
from pattern import Pattern


FILE_VERSION = 100
ENTRY_SIZE = 18

class PatternFile:

    def __init__(self):
        self.version = FILE_VERSION
        self.clearAllPatterns()
        self.reset()

    def clearAllPatterns(self):
        self.entries = []
        self.currentEntry = 0

    def seek(self, entryNum):
        self.currentEntry = entryNum

    def reset(self):
        self.currentEntry = 0

    def numEntries(self):
        return len(self.entries)

    def writeFile(self, fileName):
        f = open(fileName, 'w')

        #
        # Write the header information to disk.
        #
        f.write(a2b_hex( str('%02x' % self.version) ))
        f.write(a2b_hex( str('%04x' % len(self.entries)) ))

        #
        # Write the entries to disk
        #
        for i in range(len(self.entries)):
            f.write( self.entries[i] )
        
    def readFile(self, fileName):
        f = open(fileName, 'r')
        self.clearAllPatterns()

        #
        # Read the header information to disk.
        #
        self.version = int( b2a_hex(f.read(1)), 16 )
        numEntries = int( b2a_hex(f.read(2)) , 16 )

        #
        # Write the entries to disk
        #

        for i in range(numEntries):
            self.entries.append( f.read(ENTRY_SIZE) )

    def appendPattern(self, pattern, bank = 0, loc = 0):
        bankByte = a2b_hex( (str('%02x' % bank)))
        locByte = a2b_hex( (str('%02x' % loc)))
        self.entries.append(bankByte + locByte + pattern.toByteString())
        
    def getNextPattern(self):
        if self.currentEntry < len(self.entries):
            bank = int( b2a_hex(self.entries[self.currentEntry][0]), 16 )
            loc = int( b2a_hex(self.entries[self.currentEntry][1]), 16 )
            pattern = Pattern(self.entries[self.currentEntry][2:ENTRY_SIZE])
            
            self.currentEntry += 1;

            return [bank, loc, pattern]
        else:
            raise PatternFileException('Attempt to access out of bounds pattern.')

