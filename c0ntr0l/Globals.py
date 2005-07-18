#
# Josh Lifton and Michael Broxton
# MIT Media Lab
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
# Name:         Globals.py
# Purpose:      Global variables 
#
# Author:       Michael Broxton
#
# Created:      A long time ago, in a galaxy far, far away...
# Copyright:    (c) 2004 by MIT Media Laboratory
#----------------------------------------------------------------------------

APP_NAME = "x0xb0x c0ontr0l"

#
# Basic constants
#
NOTES_IN_PATTERN = 16
NUMBER_OF_BANKS = 16
LOCATIONS_PER_BANK = 8


SYNCMSG_OUT = 'Sync Out'
SYNCMSG_IN_MIDI = 'MIDI Sync In'
SYNCMSG_IN_DIN = 'DIN Sync In'


#
# Note and pattern related constants
#
TRANSPOSE_UP = 1
TRANSPOSE_DOWN = -1
TRANSPOSE_NONE = 0

BOTTOM_NOTE = 0x17
REST_NOTE = 0x00
NULL_NOTE = 0xFF
TOP_NOTE = 0x23

MIDI_Dict = {'C'   : 0x17,
             'C#'  : 0x18,
             'D'   : 0x19,
             'D#'  : 0x1A,
             'E'   : 0x1B,
             'F'   : 0x1C,
             'F#'  : 0x1D,
             'G'   : 0x1E,
             'G#'  : 0x1F,
             'A'   : 0x20,
             'A#'  : 0x21,
             'B'   : 0x22,
             'C\'' : 0x23 }



#
# Serial port attributes.
#
DEFAULT_BAUD_RATE = 19200
DEFAULT_COMM_PORT = '/dev/cu.usbserial-3B1'
DEFAULT_TIMEOUT = 2.0


def hexToSignedInt(hexString) :
    hexString = hexString.upper()
    if int(hexString,16) > 0x7FFF :
        twosComp = ''
        hexString = str('%04X' % (int(hexString,16) - 1))
        for c in hexString :
            twosComp = twosComp + str('%01X' % abs(int(c,16) - 15))
        return -1*int(twosComp,16)
    return int(hexString,16)

def opj(path):
    """Convert paths to the platform-specific separator"""
    return apply(os.path.join, tuple(path.split('/')))


#
# Exceptions
#
class ConfigException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PatternFileException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
